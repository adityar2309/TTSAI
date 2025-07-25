import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  InputAdornment,
  IconButton,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Collapse,
  Paper,
  CircularProgress,
  useTheme,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  KeyboardArrowDown as ExpandMoreIcon,
  KeyboardArrowUp as ExpandLessIcon,
  FlashOn as FlashOnIcon,
  Quiz as QuizIcon,
  Chat as ChatIcon,
  School as SchoolIcon,
} from '@mui/icons-material';

// Styled components
const SearchContainer = styled(Box)(({ theme }) => ({
  position: 'relative',
  width: '100%',
}));

const SearchResults = styled(Paper)(({ theme }) => ({
  position: 'absolute',
  top: '100%',
  left: 0,
  right: 0,
  zIndex: 1000,
  maxHeight: 400,
  overflow: 'auto',
  marginTop: theme.spacing(1),
}));

const CategoryHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1, 2),
  backgroundColor: theme.palette.background.default,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  cursor: 'pointer',
}));

/**
 * Search component for learning tools
 * 
 * @param {Object} props
 * @param {function} props.onSearch - Callback when search is performed
 * @param {function} props.onResultClick - Callback when a search result is clicked
 * @param {boolean} props.loading - Whether search is loading
 * @param {Object} props.results - Search results object with categories
 * @param {string} props.placeholder - Placeholder text for search field
 */
const SearchTools = ({
  onSearch,
  onResultClick,
  loading = false,
  results = null,
  placeholder = 'Search learning tools...',
}) => {
  const theme = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState({});
  
  // Initialize expanded categories
  useEffect(() => {
    if (results) {
      const categories = {};
      Object.keys(results).forEach(category => {
        categories[category] = true; // Default to expanded
      });
      setExpandedCategories(categories);
    }
  }, [results]);
  
  // Handle search input change
  const handleSearchChange = (event) => {
    const query = event.target.value;
    setSearchQuery(query);
    
    if (query.length >= 2) {
      if (onSearch) {
        onSearch(query);
      }
      setShowResults(true);
    } else {
      setShowResults(false);
    }
  };
  
  // Handle search clear
  const handleSearchClear = () => {
    setSearchQuery('');
    setShowResults(false);
  };
  
  // Handle result click
  const handleResultClick = (result) => {
    if (onResultClick) {
      onResultClick(result);
    }
    setShowResults(false);
  };
  
  // Handle category toggle
  const handleCategoryToggle = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category],
    }));
  };
  
  // Handle click outside to close results
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showResults && !event.target.closest('.search-container')) {
        setShowResults(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showResults]);
  
  // Get icon for category
  const getCategoryIcon = (category) => {
    switch (category.toLowerCase()) {
      case 'flashcards':
        return <FlashOnIcon />;
      case 'quizzes':
        return <QuizIcon />;
      case 'conversations':
        return <ChatIcon />;
      case 'lessons':
        return <SchoolIcon />;
      default:
        return <SearchIcon />;
    }
  };
  
  // Sample results for demo
  const sampleResults = {
    'Flashcards': [
      { id: 'fc1', title: 'Basic Vocabulary', description: 'Common everyday words' },
      { id: 'fc2', title: 'Travel Phrases', description: 'Essential phrases for travelers' },
    ],
    'Quizzes': [
      { id: 'q1', title: 'Grammar Basics', description: 'Test your grammar knowledge' },
      { id: 'q2', title: 'Intermediate Vocabulary', description: 'Expand your vocabulary' },
    ],
    'Conversations': [
      { id: 'c1', title: 'Restaurant Dialogue', description: 'Practice ordering food' },
    ],
  };
  
  // Use provided results or sample results
  const searchResults = results || (searchQuery.length >= 2 ? sampleResults : null);
  
  return (
    <SearchContainer className="search-container">
      <TextField
        fullWidth
        placeholder={placeholder}
        value={searchQuery}
        onChange={handleSearchChange}
        variant="outlined"
        size="medium"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon color="action" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              {loading ? (
                <CircularProgress size={20} />
              ) : searchQuery && (
                <IconButton
                  aria-label="clear search"
                  onClick={handleSearchClear}
                  edge="end"
                  size="small"
                >
                  <ClearIcon fontSize="small" />
                </IconButton>
              )}
            </InputAdornment>
          ),
          sx: {
            borderRadius: theme.shape.borderRadius * 2,
            backgroundColor: theme.palette.background.paper,
          },
        }}
      />
      
      {/* Search results */}
      {showResults && searchResults && (
        <SearchResults elevation={3}>
          {Object.keys(searchResults).length === 0 ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No results found for "{searchQuery}"
              </Typography>
            </Box>
          ) : (
            <List disablePadding>
              {Object.entries(searchResults).map(([category, items]) => (
                <React.Fragment key={category}>
                  <CategoryHeader onClick={() => handleCategoryToggle(category)}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {getCategoryIcon(category)}
                      <Typography variant="subtitle1" sx={{ ml: 1, fontWeight: 500 }}>
                        {category} ({items.length})
                      </Typography>
                    </Box>
                    {expandedCategories[category] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </CategoryHeader>
                  
                  <Collapse in={expandedCategories[category]} timeout="auto">
                    {items.map((item) => (
                      <ListItem key={item.id} disablePadding>
                        <ListItemButton onClick={() => handleResultClick(item)}>
                          <ListItemText
                            primary={item.title}
                            secondary={item.description}
                            primaryTypographyProps={{
                              variant: 'body1',
                              sx: { fontWeight: 500 },
                            }}
                          />
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </Collapse>
                </React.Fragment>
              ))}
            </List>
          )}
        </SearchResults>
      )}
    </SearchContainer>
  );
};

export default SearchTools;