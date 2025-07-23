import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  List, 
  ListItem, 
  ListItemText, 
  Divider, 
  CircularProgress, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails,
  Alert,
  Chip,
  Grid,
  TextField,
  Switch,
  FormControlLabel
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import RefreshIcon from '@mui/icons-material/Refresh';
import DownloadIcon from '@mui/icons-material/Download';
import BugReportIcon from '@mui/icons-material/BugReport';

/**
 * Frontend Diagnostic Tool Component
 * 
 * This component provides comprehensive diagnostics for the frontend application:
 * - Console error tracking and reporting
 * - Resource loading verification
 * - UI component testing
 * - API connectivity testing
 * - Performance metrics
 */
const DiagnosticTool = () => {
  // State for diagnostic results
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({
    console: { errors: [], warnings: [] },
    resources: { success: [], failed: [] },
    components: { tested: [], failed: [] },
    api: { endpoints: [], failed: [] },
    performance: { metrics: {} }
  });
  const [expanded, setExpanded] = useState('console');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [apiEndpoint, setApiEndpoint] = useState('http://localhost:5000');

  // Function to handle accordion expansion
  const handleChange = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : false);
  };

  // Function to capture console errors
  const setupConsoleErrorCapture = useCallback(() => {
    const originalConsoleError = console.error;
    const originalConsoleWarn = console.warn;
    const errors = [];
    const warnings = [];

    console.error = (...args) => {
      errors.push({
        message: args.map(arg => 
          typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
        ).join(' '),
        timestamp: new Date().toISOString()
      });
      originalConsoleError.apply(console, args);
    };

    console.warn = (...args) => {
      warnings.push({
        message: args.map(arg => 
          typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
        ).join(' '),
        timestamp: new Date().toISOString()
      });
      originalConsoleWarn.apply(console, args);
    };

    return { errors, warnings, restore: () => {
      console.error = originalConsoleError;
      console.warn = originalConsoleWarn;
    }};
  }, []);

  // Function to check resource loading
  const checkResources = useCallback(async () => {
    const resources = [];
    const success = [];
    const failed = [];

    // Get all resources from the page
    const scripts = Array.from(document.getElementsByTagName('script'));
    const links = Array.from(document.getElementsByTagName('link'));
    const images = Array.from(document.getElementsByTagName('img'));

    // Check scripts
    scripts.forEach(script => {
      const src = script.src;
      if (src) {
        resources.push({ type: 'script', url: src });
      }
    });

    // Check stylesheets and other link elements
    links.forEach(link => {
      const href = link.href;
      if (href) {
        resources.push({ type: link.rel, url: href });
      }
    });

    // Check images
    images.forEach(img => {
      const src = img.src;
      if (src) {
        resources.push({ type: 'image', url: src });
      }
    });

    // Check manifest
    const manifestLink = document.querySelector('link[rel="manifest"]');
    if (manifestLink) {
      resources.push({ type: 'manifest', url: manifestLink.href });
    }

    // Check favicon
    const faviconLink = document.querySelector('link[rel="icon"]');
    if (faviconLink) {
      resources.push({ type: 'favicon', url: faviconLink.href });
    }

    // Test each resource
    for (const resource of resources) {
      try {
        const response = await fetch(resource.url, { method: 'HEAD', mode: 'no-cors' });
        success.push({ ...resource, status: 'loaded' });
      } catch (error) {
        failed.push({ ...resource, status: 'failed', error: error.message });
      }
    }

    return { success, failed };
  }, []);

  // Function to test UI components
  const testComponents = useCallback(() => {
    const components = [];
    const failed = [];

    // Get all components with data-testid attribute
    const testableElements = document.querySelectorAll('[data-testid]');
    
    testableElements.forEach(element => {
      const componentInfo = {
        id: element.getAttribute('data-testid'),
        type: element.tagName.toLowerCase(),
        visible: element.offsetParent !== null,
        position: {
          x: element.offsetLeft,
          y: element.offsetTop,
          width: element.offsetWidth,
          height: element.offsetHeight
        }
      };
      
      components.push(componentInfo);
      
      // Check if component is properly rendered
      if (componentInfo.width === 0 || componentInfo.height === 0) {
        failed.push({
          ...componentInfo,
          error: 'Component has zero width or height'
        });
      }
      
      if (!componentInfo.visible) {
        failed.push({
          ...componentInfo,
          error: 'Component is not visible'
        });
      }
    });

    return { tested: components, failed };
  }, []);

  // Function to test API connectivity
  const testApiConnectivity = useCallback(async (baseUrl) => {
    const endpoints = [
      { name: 'Health Check', path: '/api/health', method: 'GET' },
      { name: 'Supported Languages', path: '/api/supported-languages', method: 'GET' },
      { name: 'Word of Day', path: '/api/word-of-day?language=en', method: 'GET' }
    ];
    
    const results = [];
    const failed = [];
    
    for (const endpoint of endpoints) {
      try {
        const startTime = performance.now();
        const response = await fetch(`${baseUrl}${endpoint.path}`, {
          method: endpoint.method,
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        const endTime = performance.now();
        const responseTime = endTime - startTime;
        
        const result = {
          ...endpoint,
          status: response.status,
          responseTime: responseTime.toFixed(2),
          success: response.ok
        };
        
        results.push(result);
        
        if (!response.ok) {
          failed.push({
            ...result,
            error: `HTTP ${response.status}: ${response.statusText}`
          });
        }
      } catch (error) {
        const result = {
          ...endpoint,
          status: 'error',
          error: error.message,
          success: false
        };
        
        results.push(result);
        failed.push(result);
      }
    }
    
    return { endpoints: results, failed };
  }, []);

  // Function to measure performance metrics
  const measurePerformance = useCallback(() => {
    const metrics = {};
    
    // Use Performance API if available
    if (window.performance) {
      if (window.performance.timing) {
        const timing = window.performance.timing;
        
        metrics.loadTime = timing.loadEventEnd - timing.navigationStart;
        metrics.domContentLoaded = timing.domContentLoadedEventEnd - timing.navigationStart;
        metrics.firstPaint = timing.responseEnd - timing.navigationStart;
        metrics.ttfb = timing.responseStart - timing.requestStart;
      }
      
      // Get memory info if available
      if (window.performance.memory) {
        metrics.usedJSHeapSize = window.performance.memory.usedJSHeapSize;
        metrics.totalJSHeapSize = window.performance.memory.totalJSHeapSize;
        metrics.jsHeapSizeLimit = window.performance.memory.jsHeapSizeLimit;
      }
    }
    
    // Count DOM elements
    metrics.domElements = document.getElementsByTagName('*').length;
    
    // Check for event listeners (approximate)
    metrics.eventListeners = window.getEventListeners ? 
      Object.keys(window.getEventListeners(window)).length : 'Not available';
    
    return { metrics };
  }, []);

  // Function to run all diagnostics
  const runDiagnostics = useCallback(async () => {
    setLoading(true);
    
    // Capture console errors
    const consoleCapture = setupConsoleErrorCapture();
    
    // Run diagnostics in parallel
    const [resourcesResult, componentsResult, apiResult, performanceResult] = await Promise.all([
      checkResources(),
      testComponents(),
      testApiConnectivity(apiEndpoint),
      measurePerformance()
    ]);
    
    // Restore console functions and get captured errors
    consoleCapture.restore();
    
    setResults({
      console: { 
        errors: consoleCapture.errors, 
        warnings: consoleCapture.warnings 
      },
      resources: resourcesResult,
      components: componentsResult,
      api: apiResult,
      performance: performanceResult
    });
    
    setLoading(false);
  }, [setupConsoleErrorCapture, checkResources, testComponents, testApiConnectivity, measurePerformance, apiEndpoint]);

  // Run diagnostics on mount and when autoRefresh is enabled
  useEffect(() => {
    runDiagnostics();
    
    let interval;
    if (autoRefresh) {
      interval = setInterval(runDiagnostics, 30000); // Refresh every 30 seconds
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [runDiagnostics, autoRefresh]);

  // Function to download diagnostic results
  const downloadResults = () => {
    const dataStr = JSON.stringify(results, null, 2);
    const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
    
    const exportFileDefaultName = `frontend-diagnostics-${new Date().toISOString()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Calculate summary statistics
  const summary = {
    errors: results.console.errors.length,
    warnings: results.console.warnings.length,
    failedResources: results.resources.failed.length,
    failedComponents: results.components.failed.length,
    failedApiEndpoints: results.api.failed.length,
    totalIssues: results.console.errors.length + 
                results.resources.failed.length + 
                results.components.failed.length + 
                results.api.failed.length
  };

  // Determine overall health status
  let healthStatus = 'healthy';
  if (summary.errors > 0 || summary.failedResources > 0 || summary.failedApiEndpoints > 0) {
    healthStatus = 'critical';
  } else if (summary.warnings > 0 || summary.failedComponents > 0) {
    healthStatus = 'warning';
  }

  return (
    <Box sx={{ p: 3 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <BugReportIcon sx={{ mr: 1 }} />
            <Typography variant="h5" component="h1">
              Frontend Diagnostic Tool
            </Typography>
          </Box>
          <Box>
            <FormControlLabel
              control={
                <Switch
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  color="primary"
                />
              }
              label="Auto-refresh"
            />
            <Button 
              variant="outlined" 
              startIcon={<RefreshIcon />} 
              onClick={runDiagnostics}
              disabled={loading}
              sx={{ mr: 1 }}
            >
              Refresh
            </Button>
            <Button 
              variant="outlined" 
              startIcon={<DownloadIcon />} 
              onClick={downloadResults}
              disabled={loading}
            >
              Export
            </Button>
          </Box>
        </Box>

        <Box sx={{ mb: 3 }}>
          <TextField
            label="API Endpoint"
            variant="outlined"
            fullWidth
            value={apiEndpoint}
            onChange={(e) => setApiEndpoint(e.target.value)}
            size="small"
            helperText="Enter the base URL of your backend API"
          />
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Typography variant="body1" sx={{ mr: 2 }}>
            Health Status:
          </Typography>
          {healthStatus === 'healthy' && (
            <Chip 
              icon={<CheckCircleIcon />} 
              label="Healthy" 
              color="success" 
              variant="outlined" 
            />
          )}
          {healthStatus === 'warning' && (
            <Chip 
              icon={<WarningIcon />} 
              label="Warning" 
              color="warning" 
              variant="outlined" 
            />
          )}
          {healthStatus === 'critical' && (
            <Chip 
              icon={<ErrorIcon />} 
              label="Critical" 
              color="error" 
              variant="outlined" 
            />
          )}
          
          <Box sx={{ ml: 'auto', display: 'flex', gap: 2 }}>
            <Chip 
              icon={<ErrorIcon />} 
              label={`${summary.errors} Errors`} 
              color={summary.errors > 0 ? "error" : "default"} 
              variant="outlined" 
            />
            <Chip 
              icon={<WarningIcon />} 
              label={`${summary.warnings} Warnings`} 
              color={summary.warnings > 0 ? "warning" : "default"} 
              variant="outlined" 
            />
            <Chip 
              icon={<InfoIcon />} 
              label={`${summary.totalIssues} Total Issues`} 
              color={summary.totalIssues > 0 ? "primary" : "default"} 
              variant="outlined" 
            />
          </Box>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Accordion 
              expanded={expanded === 'console'} 
              onChange={handleChange('console')}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>
                  Console Errors and Warnings 
                  {summary.errors > 0 && (
                    <Chip 
                      size="small" 
                      label={`${summary.errors} Errors`} 
                      color="error" 
                      sx={{ ml: 1 }} 
                    />
                  )}
                  {summary.warnings > 0 && (
                    <Chip 
                      size="small" 
                      label={`${summary.warnings} Warnings`} 
                      color="warning" 
                      sx={{ ml: 1 }} 
                    />
                  )}
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {results.console.errors.length === 0 && results.console.warnings.length === 0 ? (
                  <Alert severity="success">No console errors or warnings detected</Alert>
                ) : (
                  <>
                    {results.console.errors.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1" sx={{ mb: 1 }}>
                          Errors:
                        </Typography>
                        <List>
                          {results.console.errors.map((error, index) => (
                            <ListItem key={index} sx={{ bgcolor: 'error.light', borderRadius: 1, mb: 1 }}>
                              <ListItemText 
                                primary={error.message} 
                                secondary={`Timestamp: ${error.timestamp}`} 
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}
                    
                    {results.console.warnings.length > 0 && (
                      <Box>
                        <Typography variant="subtitle1" sx={{ mb: 1 }}>
                          Warnings:
                        </Typography>
                        <List>
                          {results.console.warnings.map((warning, index) => (
                            <ListItem key={index} sx={{ bgcolor: 'warning.light', borderRadius: 1, mb: 1 }}>
                              <ListItemText 
                                primary={warning.message} 
                                secondary={`Timestamp: ${warning.timestamp}`} 
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}
                  </>
                )}
              </AccordionDetails>
            </Accordion>

            <Accordion 
              expanded={expanded === 'resources'} 
              onChange={handleChange('resources')}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>
                  Resource Loading 
                  {results.resources.failed.length > 0 && (
                    <Chip 
                      size="small" 
                      label={`${results.resources.failed.length} Failed`} 
                      color="error" 
                      sx={{ ml: 1 }} 
                    />
                  )}
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {results.resources.failed.length === 0 ? (
                  <Alert severity="success">All resources loaded successfully</Alert>
                ) : (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" sx={{ mb: 1 }}>
                      Failed Resources:
                    </Typography>
                    <List>
                      {results.resources.failed.map((resource, index) => (
                        <ListItem key={index} sx={{ bgcolor: 'error.light', borderRadius: 1, mb: 1 }}>
                          <ListItemText 
                            primary={`${resource.type}: ${resource.url}`} 
                            secondary={`Error: ${resource.error}`} 
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
                
                <Typography variant="subtitle1" sx={{ mb: 1, mt: 2 }}>
                  Successful Resources:
                </Typography>
                <List>
                  {results.resources.success.map((resource, index) => (
                    <ListItem key={index}>
                      <ListItemText 
                        primary={resource.type} 
                        secondary={resource.url} 
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>

            <Accordion 
              expanded={expanded === 'components'} 
              onChange={handleChange('components')}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>
                  UI Components 
                  {results.components.failed.length > 0 && (
                    <Chip 
                      size="small" 
                      label={`${results.components.failed.length} Issues`} 
                      color="warning" 
                      sx={{ ml: 1 }} 
                    />
                  )}
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {results.components.tested.length === 0 ? (
                  <Alert severity="info">No testable components found. Add data-testid attributes to your components.</Alert>
                ) : (
                  <>
                    {results.components.failed.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1" sx={{ mb: 1 }}>
                          Component Issues:
                        </Typography>
                        <List>
                          {results.components.failed.map((component, index) => (
                            <ListItem key={index} sx={{ bgcolor: 'warning.light', borderRadius: 1, mb: 1 }}>
                              <ListItemText 
                                primary={`${component.type} (${component.id})`} 
                                secondary={`Error: ${component.error}`} 
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}
                    
                    <Typography variant="subtitle1" sx={{ mb: 1 }}>
                      Tested Components:
                    </Typography>
                    <Grid container spacing={2}>
                      {results.components.tested.map((component, index) => (
                        <Grid item xs={12} sm={6} md={4} key={index}>
                          <Paper sx={{ p: 2 }}>
                            <Typography variant="subtitle2">
                              {component.id} ({component.type})
                            </Typography>
                            <Typography variant="body2">
                              Visible: {component.visible ? 'Yes' : 'No'}
                            </Typography>
                            <Typography variant="body2">
                              Size: {component.position.width}x{component.position.height}
                            </Typography>
                            <Typography variant="body2">
                              Position: ({component.position.x}, {component.position.y})
                            </Typography>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </>
                )}
              </AccordionDetails>
            </Accordion>

            <Accordion 
              expanded={expanded === 'api'} 
              onChange={handleChange('api')}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>
                  API Connectivity 
                  {results.api.failed.length > 0 && (
                    <Chip 
                      size="small" 
                      label={`${results.api.failed.length} Failed`} 
                      color="error" 
                      sx={{ ml: 1 }} 
                    />
                  )}
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {results.api.endpoints.length === 0 ? (
                  <Alert severity="info">No API endpoints tested</Alert>
                ) : (
                  <List>
                    {results.api.endpoints.map((endpoint, index) => (
                      <React.Fragment key={index}>
                        <ListItem>
                          <ListItemText 
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                {endpoint.success ? (
                                  <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                                ) : (
                                  <ErrorIcon color="error" sx={{ mr: 1 }} />
                                )}
                                {endpoint.name}
                              </Box>
                            } 
                            secondary={
                              <>
                                <Typography variant="body2">
                                  {`${endpoint.method} ${endpoint.path}`}
                                </Typography>
                                {endpoint.status && (
                                  <Typography variant="body2">
                                    Status: {endpoint.status}
                                  </Typography>
                                )}
                                {endpoint.responseTime && (
                                  <Typography variant="body2">
                                    Response Time: {endpoint.responseTime}ms
                                  </Typography>
                                )}
                                {endpoint.error && (
                                  <Typography variant="body2" color="error">
                                    Error: {endpoint.error}
                                  </Typography>
                                )}
                              </>
                            } 
                          />
                        </ListItem>
                        {index < results.api.endpoints.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </AccordionDetails>
            </Accordion>

            <Accordion 
              expanded={expanded === 'performance'} 
              onChange={handleChange('performance')}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>Performance Metrics</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  {Object.entries(results.performance.metrics).map(([key, value]) => (
                    <Grid item xs={12} sm={6} md={4} key={key}>
                      <Paper sx={{ p: 2 }}>
                        <Typography variant="subtitle2">
                          {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                        </Typography>
                        <Typography variant="body1">
                          {typeof value === 'number' && key.includes('time') ? 
                            `${value}ms` : 
                            typeof value === 'number' && (key.includes('Size') || key.includes('Limit')) ?
                              `${Math.round(value / (1024 * 1024))} MB` :
                              value
                          }
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </AccordionDetails>
            </Accordion>
          </>
        )}
      </Paper>
    </Box>
  );
};

export default DiagnosticTool;