import React from 'react';
import { Box, Container, useTheme, useMediaQuery } from '@mui/material';
import { styled } from '@mui/material/styles';

// Styled component for the main container
const StyledContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(2),
  },
}));

/**
 * Main container component for the learning tools page
 * Provides responsive layout and consistent spacing
 */
const ToolsContainer = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  return (
    <Container maxWidth="xl">
      <StyledContainer
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: isMobile ? 2 : 3,
        }}
      >
        {children}
      </StyledContainer>
    </Container>
  );
};

export default ToolsContainer;