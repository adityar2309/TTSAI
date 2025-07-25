import React from 'react';
import { Grid, Box, useTheme, useMediaQuery } from '@mui/material';
import { styled } from '@mui/material/styles';

// Styled component for grid container with animation
const AnimatedGrid = styled(Grid)(({ theme }) => ({
  '& .grid-item': {
    transition: 'transform 0.3s ease, box-shadow 0.3s ease',
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: theme.shadows[6],
    },
  },
}));

/**
 * Responsive grid system for learning tools
 * Automatically adjusts columns based on screen size
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Grid items to display
 * @param {number} props.spacing - Grid spacing (default: 3)
 * @param {number} props.xs - Columns on extra small screens (default: 12)
 * @param {number} props.sm - Columns on small screens (default: 6)
 * @param {number} props.md - Columns on medium screens (default: 4)
 * @param {number} props.lg - Columns on large screens (default: 3)
 * @param {boolean} props.animated - Whether to animate grid items on hover (default: true)
 */
const ResponsiveGrid = ({
  children,
  spacing = 3,
  xs = 12,
  sm = 6,
  md = 4,
  lg = 3,
  animated = true,
  ...props
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // If no children or empty array, return null
  if (!children || (Array.isArray(children) && children.length === 0)) {
    return null;
  }
  
  // Convert single child to array for consistent mapping
  const childrenArray = React.Children.toArray(children);
  
  return (
    <Box sx={{ width: '100%' }}>
      <AnimatedGrid container spacing={isMobile ? 2 : spacing} {...props}>
        {childrenArray.map((child, index) => (
          <Grid
            item
            xs={xs}
            sm={sm}
            md={md}
            lg={lg}
            key={index}
            className={animated ? 'grid-item' : ''}
          >
            {child}
          </Grid>
        ))}
      </AnimatedGrid>
    </Box>
  );
};

export default ResponsiveGrid;