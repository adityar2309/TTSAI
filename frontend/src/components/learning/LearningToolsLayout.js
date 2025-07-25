import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  useTheme,
  useMediaQuery,
  Drawer,
  IconButton,
  Fab,
  Divider,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  ArrowUpward as ArrowUpwardIcon,
} from '@mui/icons-material';

// Styled components
const MainContent = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  transition: theme.transitions.create('margin', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
}));

const SidebarContent = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
  overflow: 'auto',
}));

const ScrollToTopButton = styled(Fab)(({ theme }) => ({
  position: 'fixed',
  bottom: theme.spacing(2),
  right: theme.spacing(2),
  zIndex: 1000,
}));

/**
 * Responsive layout for the learning tools page
 * Provides sidebar, main content area, and responsive behavior
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.sidebar - Sidebar content
 * @param {React.ReactNode} props.main - Main content
 * @param {boolean} props.sidebarOpen - Whether sidebar is open (for controlled component)
 * @param {function} props.onSidebarToggle - Callback when sidebar is toggled
 * @param {string} props.sidebarWidth - Width of sidebar (default: '280px')
 */
const LearningToolsLayout = ({
  sidebar,
  main,
  sidebarOpen: controlledSidebarOpen,
  onSidebarToggle,
  sidebarWidth = '280px',
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [internalSidebarOpen, setInternalSidebarOpen] = useState(!isMobile);
  const [showScrollTop, setShowScrollTop] = useState(false);
  
  // Determine if component is controlled or uncontrolled
  const isControlled = controlledSidebarOpen !== undefined;
  const sidebarOpen = isControlled ? controlledSidebarOpen : internalSidebarOpen;
  
  // Handle sidebar toggle
  const handleSidebarToggle = () => {
    if (isControlled) {
      onSidebarToggle?.(!sidebarOpen);
    } else {
      setInternalSidebarOpen(!sidebarOpen);
    }
  };
  
  // Close sidebar on mobile when component mounts
  useEffect(() => {
    if (isMobile && !isControlled) {
      setInternalSidebarOpen(false);
    }
  }, [isMobile, isControlled]);
  
  // Handle scroll to top visibility
  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.pageYOffset > 300);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  
  // Scroll to top function
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };
  
  return (
    <Box sx={{ display: 'flex', minHeight: 'calc(100vh - 64px)' }}>
      {/* Sidebar - Persistent on desktop, drawer on mobile */}
      {isMobile ? (
        <Drawer
          variant="temporary"
          open={sidebarOpen}
          onClose={handleSidebarToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            '& .MuiDrawer-paper': {
              width: sidebarWidth,
              boxSizing: 'border-box',
            },
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', p: 1 }}>
            <IconButton onClick={handleSidebarToggle}>
              <CloseIcon />
            </IconButton>
          </Box>
          <Divider />
          <SidebarContent elevation={0}>
            {sidebar}
          </SidebarContent>
        </Drawer>
      ) : (
        <Box
          component="aside"
          sx={{
            width: sidebarOpen ? sidebarWidth : 0,
            flexShrink: 0,
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
            overflow: 'hidden',
          }}
        >
          <SidebarContent
            elevation={3}
            sx={{
              width: sidebarWidth,
              position: 'sticky',
              top: '64px', // Adjust based on your header height
            }}
          >
            {sidebar}
          </SidebarContent>
        </Box>
      )}
      
      {/* Main content */}
      <MainContent
        sx={{
          marginLeft: !isMobile && sidebarOpen ? '0' : '0',
          width: '100%',
        }}
      >
        {/* Mobile menu toggle */}
        {isMobile && (
          <Box sx={{ p: 1 }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleSidebarToggle}
              sx={{ mr: 2, display: { md: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
          </Box>
        )}
        
        {/* Main content area */}
        <Box sx={{ p: isMobile ? 1 : 2 }}>
          {main}
        </Box>
      </MainContent>
      
      {/* Scroll to top button */}
      {showScrollTop && (
        <ScrollToTopButton
          size="small"
          color="primary"
          aria-label="scroll to top"
          onClick={scrollToTop}
        >
          <ArrowUpwardIcon />
        </ScrollToTopButton>
      )}
    </Box>
  );
};

export default LearningToolsLayout;