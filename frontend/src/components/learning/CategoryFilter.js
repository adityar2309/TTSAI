import React, { useState } from 'react';
import {
  Box,
  Chip,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  useTheme,
  useMediaQuery,
  Paper,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  MoreHoriz as MoreIcon,
  Check as CheckIcon,
} from '@mui/icons-material';

// Styled components
const CategoryContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(1.5),
  marginBottom: theme.spacing(3),
  display: 'flex',
  alignItems: 'center',
  overflowX: 'auto',
  scrollbarWidth: 'none', // Firefox
  '&::-webkit-scrollbar': {
    display: 'none', // Chrome, Safari, Opera
  },
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(1),
  },
}));

const ChipContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  flexWrap: 'nowrap',
  paddingRight: theme.spacing(1),
}));

/**
 * Category filter component for learning tools
 * 
 * @param {Object} props
 * @param {string} props.activeCategory - Currently active category
 * @param {function} props.onCategoryChange - Callback when category changes
 * @param {Array} props.categories - Array of category objects with id, label, icon, color
 * @param {string} props.label - Label for the filter (default: 'Categories')
 */
const CategoryFilter = ({
  activeCategory = 'all',
  onCategoryChange,
  categories = [],
  label = 'Categories',
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [moreMenuAnchor, setMoreMenuAnchor] = useState(null);
  
  // Default categories if none provided
  const defaultCategories = [
    { id: 'all', label: 'All', color: 'default' },
    { id: 'vocabulary', label: 'Vocabulary', color: 'primary' },
    { id: 'grammar', label: 'Grammar', color: 'secondary' },
    { id: 'conversation', label: 'Conversation', color: 'success' },
    { id: 'reading', label: 'Reading', color: 'info' },
    { id: 'writing', label: 'Writing', color: 'warning' },
    { id: 'listening', label: 'Listening', color: 'error' },
  ];
  
  // Use provided categories or default categories
  const filterCategories = categories.length > 0 ? categories : defaultCategories;
  
  // Determine which categories to show in the more menu based on screen size
  const visibleCount = isMobile ? 3 : 6;
  const visibleCategories = filterCategories.slice(0, visibleCount);
  const moreCategories = filterCategories.slice(visibleCount);
  
  // Handle category change
  const handleCategoryChange = (categoryId) => {
    if (onCategoryChange) {
      onCategoryChange(categoryId);
    }
  };
  
  // Handle more menu open
  const handleMoreMenuOpen = (event) => {
    setMoreMenuAnchor(event.currentTarget);
  };
  
  // Handle more menu close
  const handleMoreMenuClose = () => {
    setMoreMenuAnchor(null);
  };
  
  // Handle more menu item click
  const handleMoreMenuItemClick = (categoryId) => {
    handleCategoryChange(categoryId);
    handleMoreMenuClose();
  };
  
  return (
    <CategoryContainer elevation={1}>
      {!isMobile && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mr: 2, whiteSpace: 'nowrap' }}
        >
          {label}:
        </Typography>
      )}
      
      <ChipContainer>
        {visibleCategories.map((category) => (
          <Chip
            key={category.id}
            label={category.label}
            icon={category.icon}
            color={category.color || 'default'}
            variant={activeCategory === category.id ? 'filled' : 'outlined'}
            onClick={() => handleCategoryChange(category.id)}
            clickable
          />
        ))}
        
        {moreCategories.length > 0 && (
          <Box>
            <Tooltip title="More categories">
              <IconButton
                size="small"
                onClick={handleMoreMenuOpen}
                aria-label="more categories"
                aria-controls="category-menu"
                aria-haspopup="true"
              >
                <MoreIcon />
              </IconButton>
            </Tooltip>
            
            <Menu
              id="category-menu"
              anchorEl={moreMenuAnchor}
              keepMounted
              open={Boolean(moreMenuAnchor)}
              onClose={handleMoreMenuClose}
            >
              {moreCategories.map((category) => (
                <MenuItem
                  key={category.id}
                  onClick={() => handleMoreMenuItemClick(category.id)}
                  selected={activeCategory === category.id}
                >
                  {category.label}
                  {activeCategory === category.id && (
                    <CheckIcon fontSize="small" sx={{ ml: 1 }} />
                  )}
                </MenuItem>
              ))}
            </Menu>
          </Box>
        )}
      </ChipContainer>
    </CategoryContainer>
  );
};

export default CategoryFilter;