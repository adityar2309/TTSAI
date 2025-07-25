import React from 'react';
import { Box, useTheme, useMediaQuery, Paper } from '@mui/material';
import { styled } from '@mui/material/styles';

// Styled components for mobile-friendly design
const MobileContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(1),
  },
}));

const MobileCard = styled(Paper)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius * 2,
  overflow: 'hidden',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  [theme.breakpoints.down('sm')]: {
    borderRadius: theme.shape.borderRadius,
  },
}));

/**
 * Mobile-responsive container component
 * Adjusts padding, spacing, and styling based on screen size
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Content to display
 * @param {boolean} props.fullWidth - Whether to use full width (default: false)
 * @param {boolean} props.noGutters - Whether to remove padding (default: false)
 * @param {boolean} props.card - Whether to wrap content in a card (default: false)
 * @param {Object} props.sx - Additional styles to apply
 */
const MobileResponsiveContainer = ({
  children,
  fullWidth = false,
  noGutters = false,
  card = false,
  sx = {},
  ...props
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Base container styles
  const containerStyles = {
    width: fullWidth ? '100%' : 'auto',
    padding: noGutters ? 0 : undefined,
    ...sx,
  };
  
  // If card is true, wrap content in a card
  if (card) {
    return (
      <MobileContainer sx={containerStyles} {...props}>
        <MobileCard
          elevation={isMobile ? 1 : 3}
          sx={{
            p: isMobile ? 2 : 3,
          }}
        >
          {children}
        </MobileCard>
      </MobileContainer>
    );
  }
  
  // Otherwise, just return the container
  return (
    <MobileContainer sx={containerStyles} {...props}>
      {children}
    </MobileContainer>
  );
};

export default MobileResponsiveContainer;