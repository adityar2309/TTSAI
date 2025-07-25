import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Divider,
  useTheme,
  useMediaQuery,
  Paper,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Dashboard as DashboardIcon,
  FlashOn as FlashOnIcon,
  Quiz as QuizIcon,
  Chat as ChatIcon,
  MoreVert as MoreVertIcon,
  FilterList as FilterListIcon,
} from '@mui/icons-material';

// Styled components
const StyledTabs = styled(Tabs)(({ theme }) => ({
  minHeight: 48,
  '& .MuiTab-root': {
    minHeight: 48,
    textTransform: 'none',
    fontWeight: 500,
  },
}));

const StyledTab = styled(Tab)(({ theme }) => ({
  minWidth: 'auto',
  padding: theme.spacing(1, 2),
}));

/**
 * Navigation component for learning tools page
 * 
 * @param {Object} props
 * @param {string} props.activeTab - Currently active tab
 * @param {function} props.onTabChange - Callback when tab changes
 * @param {Array} props.tabs - Array of tab objects with id, label, icon
 * @param {Array} props.filters - Array of filter objects with id, label
 * @param {function} props.onFilterChange - Callback when filter changes
 * @param {string} props.activeFilter - Currently active filter
 */
const ToolsNavigation = ({
  activeTab = 'dashboard',
  onTabChange,
  tabs = [],
  filters = [],
  onFilterChange,
  activeFilter = 'all',
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  
  const [moreMenuAnchor, setMoreMenuAnchor] = useState(null);
  const [filterMenuAnchor, setFilterMenuAnchor] = useState(null);
  
  // Default tabs if none provided
  const defaultTabs = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'flashcards', label: 'Flashcards', icon: <FlashOnIcon /> },
    { id: 'quizzes', label: 'Quizzes', icon: <QuizIcon /> },
    { id: 'conversation', label: 'Conversation', icon: <ChatIcon /> },
  ];
  
  // Use provided tabs or default tabs
  const navigationTabs = tabs.length > 0 ? tabs : defaultTabs;
  
  // Default filters if none provided
  const defaultFilters = [
    { id: 'all', label: 'All' },
    { id: 'recent', label: 'Recent' },
    { id: 'favorites', label: 'Favorites' },
    { id: 'completed', label: 'Completed' },
  ];
  
  // Use provided filters or default filters
  const navigationFilters = filters.length > 0 ? filters : defaultFilters;
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    if (onTabChange) {
      onTabChange(newValue);
    }
  };
  
  // Handle filter change
  const handleFilterChange = (filterId) => {
    if (onFilterChange) {
      onFilterChange(filterId);
    }
    setFilterMenuAnchor(null);
  };
  
  // Handle more menu open
  const handleMoreMenuOpen = (event) => {
    setMoreMenuAnchor(event.currentTarget);
  };
  
  // Handle more menu close
  const handleMoreMenuClose = () => {
    setMoreMenuAnchor(null);
  };
  
  // Handle filter menu open
  const handleFilterMenuOpen = (event) => {
    setFilterMenuAnchor(event.currentTarget);
  };
  
  // Handle filter menu close
  const handleFilterMenuClose = () => {
    setFilterMenuAnchor(null);
  };
  
  // Determine which tabs to show in the more menu
  const visibleTabs = isMobile ? navigationTabs.slice(0, 2) : isTablet ? navigationTabs.slice(0, 3) : navigationTabs;
  const moreTabs = isMobile ? navigationTabs.slice(2) : isTablet ? navigationTabs.slice(3) : [];
  
  return (
    <Paper elevation={1} sx={{ mb: 3, borderRadius: 2, overflow: 'hidden' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {/* Main tabs */}
        <StyledTabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          aria-label="learning tools navigation"
          sx={{ flex: 1 }}
        >
          {visibleTabs.map((tab) => (
            <StyledTab
              key={tab.id}
              value={tab.id}
              label={!isMobile ? tab.label : undefined}
              icon={tab.icon}
              iconPosition={!isMobile ? 'start' : 'top'}
              aria-label={tab.label}
            />
          ))}
        </StyledTabs>
        
        {/* More menu for mobile */}
        {moreTabs.length > 0 && (
          <>
            <IconButton
              aria-label="more tabs"
              aria-controls="more-tabs-menu"
              aria-haspopup="true"
              onClick={handleMoreMenuOpen}
              size="small"
              sx={{ mx: 1 }}
            >
              <MoreVertIcon />
            </IconButton>
            
            <Menu
              id="more-tabs-menu"
              anchorEl={moreMenuAnchor}
              keepMounted
              open={Boolean(moreMenuAnchor)}
              onClose={handleMoreMenuClose}
            >
              {moreTabs.map((tab) => (
                <MenuItem
                  key={tab.id}
                  selected={activeTab === tab.id}
                  onClick={() => {
                    handleTabChange(null, tab.id);
                    handleMoreMenuClose();
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {tab.icon && <Box sx={{ mr: 1 }}>{tab.icon}</Box>}
                    {tab.label}
                  </Box>
                </MenuItem>
              ))}
            </Menu>
          </>
        )}
        
        {/* Filter button and menu */}
        <Box sx={{ display: 'flex', alignItems: 'center', px: 1 }}>
          <Divider orientation="vertical" flexItem sx={{ mr: 1, display: { xs: 'none', sm: 'block' } }} />
          
          {isMobile ? (
            <>
              <IconButton
                aria-label="filter"
                aria-controls="filter-menu"
                aria-haspopup="true"
                onClick={handleFilterMenuOpen}
                size="small"
              >
                <FilterListIcon />
              </IconButton>
              
              <Menu
                id="filter-menu"
                anchorEl={filterMenuAnchor}
                keepMounted
                open={Boolean(filterMenuAnchor)}
                onClose={handleFilterMenuClose}
              >
                {navigationFilters.map((filter) => (
                  <MenuItem
                    key={filter.id}
                    selected={activeFilter === filter.id}
                    onClick={() => handleFilterChange(filter.id)}
                  >
                    {filter.label}
                  </MenuItem>
                ))}
              </Menu>
            </>
          ) : (
            <Box sx={{ display: 'flex', gap: 1 }}>
              {navigationFilters.map((filter) => (
                <Button
                  key={filter.id}
                  size="small"
                  color={activeFilter === filter.id ? 'primary' : 'inherit'}
                  variant={activeFilter === filter.id ? 'contained' : 'text'}
                  onClick={() => handleFilterChange(filter.id)}
                  sx={{ minWidth: 'auto' }}
                >
                  {filter.label}
                </Button>
              ))}
            </Box>
          )}
        </Box>
      </Box>
    </Paper>
  );
};

export default ToolsNavigation;