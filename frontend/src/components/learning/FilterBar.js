import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  InputAdornment,
  IconButton,
  Chip,
  Stack,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  FilterList as FilterListIcon,
  Sort as SortIcon,
  CheckCircle as CheckCircleIcon,
  ArrowDownward as ArrowDownwardIcon,
  ArrowUpward as ArrowUpwardIcon,
} from '@mui/icons-material';

// Styled components
const StyledFilterBar = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(1.5),
  marginBottom: theme.spacing(3),
  display: 'flex',
  alignItems: 'center',
  flexWrap: 'wrap',
  gap: theme.spacing(1),
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(1),
  },
}));

const StyledSearchField = styled(TextField)(({ theme }) => ({
  flexGrow: 1,
  '& .MuiOutlinedInput-root': {
    borderRadius: theme.shape.borderRadius * 2,
  },
}));

/**
 * Filter bar component for learning tools
 * 
 * @param {Object} props
 * @param {string} props.searchQuery - Current search query
 * @param {function} props.onSearchChange - Callback when search query changes
 * @param {Array} props.filters - Array of active filters
 * @param {function} props.onFilterChange - Callback when filters change
 * @param {Array} props.availableFilters - Array of available filter objects with id, label, icon
 * @param {string} props.sortBy - Current sort field
 * @param {string} props.sortDirection - Current sort direction ('asc' or 'desc')
 * @param {function} props.onSortChange - Callback when sort changes
 * @param {Array} props.availableSorts - Array of available sort options with id, label
 */
const FilterBar = ({
  searchQuery = '',
  onSearchChange,
  filters = [],
  onFilterChange,
  availableFilters = [],
  sortBy = 'name',
  sortDirection = 'asc',
  onSortChange,
  availableSorts = [],
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [filterMenuAnchor, setFilterMenuAnchor] = useState(null);
  const [sortMenuAnchor, setSortMenuAnchor] = useState(null);
  
  // Default filters if none provided
  const defaultFilters = [
    { id: 'beginner', label: 'Beginner', icon: <CheckCircleIcon sx={{ color: theme.palette.success.main }} /> },
    { id: 'intermediate', label: 'Intermediate', icon: <CheckCircleIcon sx={{ color: theme.palette.warning.main }} /> },
    { id: 'advanced', label: 'Advanced', icon: <CheckCircleIcon sx={{ color: theme.palette.error.main }} /> },
  ];
  
  // Use provided filters or default filters
  const filterOptions = availableFilters.length > 0 ? availableFilters : defaultFilters;
  
  // Default sorts if none provided
  const defaultSorts = [
    { id: 'name', label: 'Name' },
    { id: 'date', label: 'Date' },
    { id: 'difficulty', label: 'Difficulty' },
    { id: 'progress', label: 'Progress' },
  ];
  
  // Use provided sorts or default sorts
  const sortOptions = availableSorts.length > 0 ? availableSorts : defaultSorts;
  
  // Handle search change
  const handleSearchChange = (event) => {
    if (onSearchChange) {
      onSearchChange(event.target.value);
    }
  };
  
  // Handle search clear
  const handleSearchClear = () => {
    if (onSearchChange) {
      onSearchChange('');
    }
  };
  
  // Handle filter menu open
  const handleFilterMenuOpen = (event) => {
    setFilterMenuAnchor(event.currentTarget);
  };
  
  // Handle filter menu close
  const handleFilterMenuClose = () => {
    setFilterMenuAnchor(null);
  };
  
  // Handle filter toggle
  const handleFilterToggle = (filterId) => {
    if (onFilterChange) {
      const newFilters = filters.includes(filterId)
        ? filters.filter(id => id !== filterId)
        : [...filters, filterId];
      
      onFilterChange(newFilters);
    }
  };
  
  // Handle sort menu open
  const handleSortMenuOpen = (event) => {
    setSortMenuAnchor(event.currentTarget);
  };
  
  // Handle sort menu close
  const handleSortMenuClose = () => {
    setSortMenuAnchor(null);
  };
  
  // Handle sort change
  const handleSortChange = (sortId) => {
    if (onSortChange) {
      // If clicking the same sort field, toggle direction
      const newDirection = sortId === sortBy ? (sortDirection === 'asc' ? 'desc' : 'asc') : 'asc';
      onSortChange(sortId, newDirection);
    }
    handleSortMenuClose();
  };
  
  // Handle filter chip delete
  const handleFilterDelete = (filterId) => {
    if (onFilterChange) {
      const newFilters = filters.filter(id => id !== filterId);
      onFilterChange(newFilters);
    }
  };
  
  // Get current sort label
  const currentSortOption = sortOptions.find(option => option.id === sortBy) || sortOptions[0];
  
  return (
    <StyledFilterBar elevation={1}>
      {/* Search field */}
      <StyledSearchField
        placeholder="Search tools..."
        size="small"
        value={searchQuery}
        onChange={handleSearchChange}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon color="action" />
            </InputAdornment>
          ),
          endAdornment: searchQuery && (
            <InputAdornment position="end">
              <IconButton
                aria-label="clear search"
                onClick={handleSearchClear}
                edge="end"
                size="small"
              >
                <ClearIcon fontSize="small" />
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
      
      {/* Filter button */}
      <IconButton
        aria-label="filter options"
        aria-controls="filter-menu"
        aria-haspopup="true"
        onClick={handleFilterMenuOpen}
        color={filters.length > 0 ? 'primary' : 'default'}
      >
        <FilterListIcon />
      </IconButton>
      
      {/* Sort button */}
      <IconButton
        aria-label="sort options"
        aria-controls="sort-menu"
        aria-haspopup="true"
        onClick={handleSortMenuOpen}
      >
        <SortIcon />
      </IconButton>
      
      {/* Filter menu */}
      <Menu
        id="filter-menu"
        anchorEl={filterMenuAnchor}
        keepMounted
        open={Boolean(filterMenuAnchor)}
        onClose={handleFilterMenuClose}
      >
        <Typography variant="subtitle2" sx={{ px: 2, py: 1 }}>
          Filter By
        </Typography>
        <Divider />
        {filterOptions.map((filter) => (
          <MenuItem
            key={filter.id}
            onClick={() => handleFilterToggle(filter.id)}
            selected={filters.includes(filter.id)}
          >
            {filter.icon && <ListItemIcon>{filter.icon}</ListItemIcon>}
            <ListItemText primary={filter.label} />
            {filters.includes(filter.id) && <CheckCircleIcon fontSize="small" color="primary" sx={{ ml: 1 }} />}
          </MenuItem>
        ))}
      </Menu>
      
      {/* Sort menu */}
      <Menu
        id="sort-menu"
        anchorEl={sortMenuAnchor}
        keepMounted
        open={Boolean(sortMenuAnchor)}
        onClose={handleSortMenuClose}
      >
        <Typography variant="subtitle2" sx={{ px: 2, py: 1 }}>
          Sort By
        </Typography>
        <Divider />
        {sortOptions.map((sort) => (
          <MenuItem
            key={sort.id}
            onClick={() => handleSortChange(sort.id)}
            selected={sortBy === sort.id}
          >
            <ListItemText primary={sort.label} />
            {sortBy === sort.id && (
              <ListItemIcon sx={{ minWidth: 'auto' }}>
                {sortDirection === 'asc' ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />}
              </ListItemIcon>
            )}
          </MenuItem>
        ))}
      </Menu>
      
      {/* Active filters */}
      {filters.length > 0 && !isMobile && (
        <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
          <Divider orientation="vertical" flexItem />
          <Stack direction="row" spacing={1} flexWrap="wrap">
            {filters.map((filterId) => {
              const filter = filterOptions.find(f => f.id === filterId);
              return filter ? (
                <Chip
                  key={filterId}
                  label={filter.label}
                  size="small"
                  onDelete={() => handleFilterDelete(filterId)}
                  icon={filter.icon}
                />
              ) : null;
            })}
          </Stack>
        </Box>
      )}
    </StyledFilterBar>
  );
};

export default FilterBar;