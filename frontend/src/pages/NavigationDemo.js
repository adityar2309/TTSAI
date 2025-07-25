import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  Divider,
  Grid,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  FlashOn as FlashOnIcon,
  Quiz as QuizIcon,
  Chat as ChatIcon,
  School as SchoolIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

// Import components
import ToolsNavigation from '../components/learning/ToolsNavigation';
import FilterBar from '../components/learning/FilterBar';
import SearchTools from '../components/learning/SearchTools';
import CategoryFilter from '../components/learning/CategoryFilter';

/**
 * Demo page to showcase navigation and filtering components
 */
const NavigationDemo = () => {
  // State for navigation
  const [activeTab, setActiveTab] = useState('dashboard');
  const [activeFilter, setActiveFilter] = useState('all');
  
  // State for filter bar
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState([]);
  const [sortBy, setSortBy] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');
  
  // State for category filter
  const [activeCategory, setActiveCategory] = useState('all');
  
  // State for search
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  
  // Navigation tabs
  const navigationTabs = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'flashcards', label: 'Flashcards', icon: <FlashOnIcon /> },
    { id: 'quizzes', label: 'Quizzes', icon: <QuizIcon /> },
    { id: 'conversation', label: 'Conversation', icon: <ChatIcon /> },
    { id: 'lessons', label: 'Lessons', icon: <SchoolIcon /> },
    { id: 'settings', label: 'Settings', icon: <SettingsIcon /> },
  ];
  
  // Navigation filters
  const navigationFilters = [
    { id: 'all', label: 'All' },
    { id: 'recent', label: 'Recent' },
    { id: 'favorites', label: 'Favorites' },
    { id: 'completed', label: 'Completed' },
    { id: 'in-progress', label: 'In Progress' },
  ];
  
  // Available filters for filter bar
  const availableFilters = [
    { id: 'beginner', label: 'Beginner' },
    { id: 'intermediate', label: 'Intermediate' },
    { id: 'advanced', label: 'Advanced' },
    { id: 'favorite', label: 'Favorite' },
    { id: 'completed', label: 'Completed' },
  ];
  
  // Available sorts for filter bar
  const availableSorts = [
    { id: 'name', label: 'Name' },
    { id: 'date', label: 'Date Created' },
    { id: 'difficulty', label: 'Difficulty' },
    { id: 'progress', label: 'Progress' },
    { id: 'score', label: 'Best Score' },
  ];
  
  // Categories for category filter
  const categories = [
    { id: 'all', label: 'All', color: 'default' },
    { id: 'vocabulary', label: 'Vocabulary', color: 'primary' },
    { id: 'grammar', label: 'Grammar', color: 'secondary' },
    { id: 'conversation', label: 'Conversation', color: 'success' },
    { id: 'reading', label: 'Reading', color: 'info' },
    { id: 'writing', label: 'Writing', color: 'warning' },
    { id: 'listening', label: 'Listening', color: 'error' },
    { id: 'pronunciation', label: 'Pronunciation', color: 'primary' },
  ];
  
  // Handle search
  const handleSearch = (query) => {
    setSearchLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      if (query.length >= 2) {
        setSearchResults({
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
        });
      } else {
        setSearchResults(null);
      }
      setSearchLoading(false);
    }, 500);
  };
  
  // Handle search result click
  const handleSearchResultClick = (result) => {
    console.log('Search result clicked:', result);
  };
  
  // Handle sort change
  const handleSortChange = (sortField, direction) => {
    setSortBy(sortField);
    setSortDirection(direction);
    console.log('Sort changed:', sortField, direction);
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Navigation and Filtering Components
      </Typography>
      <Typography variant="body1" paragraph>
        This page demonstrates the navigation and filtering components for the learning tools page.
      </Typography>
      
      {/* Tools Navigation */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Tools Navigation
        </Typography>
        <Typography variant="body2" paragraph>
          Responsive navigation with tabs and filters. On mobile, extra tabs move to a "more" menu.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <ToolsNavigation
          activeTab={activeTab}
          onTabChange={setActiveTab}
          tabs={navigationTabs}
          filters={navigationFilters}
          onFilterChange={setActiveFilter}
          activeFilter={activeFilter}
        />
        
        <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="body2">
            Active Tab: <strong>{activeTab}</strong> | Active Filter: <strong>{activeFilter}</strong>
          </Typography>
        </Box>
      </Paper>
      
      {/* Filter Bar */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Filter Bar
        </Typography>
        <Typography variant="body2" paragraph>
          Advanced filtering with search, multiple filters, and sorting options.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <FilterBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          filters={filters}
          onFilterChange={setFilters}
          availableFilters={availableFilters}
          sortBy={sortBy}
          sortDirection={sortDirection}
          onSortChange={handleSortChange}
          availableSorts={availableSorts}
        />
        
        <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="body2">
            Search: <strong>{searchQuery || 'None'}</strong> | 
            Filters: <strong>{filters.length > 0 ? filters.join(', ') : 'None'}</strong> | 
            Sort: <strong>{sortBy} ({sortDirection})</strong>
          </Typography>
        </Box>
      </Paper>
      
      {/* Search Tools */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Search Tools
        </Typography>
        <Typography variant="body2" paragraph>
          Advanced search with categorized results and autocomplete functionality.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <SearchTools
          onSearch={handleSearch}
          onResultClick={handleSearchResultClick}
          loading={searchLoading}
          results={searchResults}
          placeholder="Search for flashcards, quizzes, conversations..."
        />
      </Paper>
      
      {/* Category Filter */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Category Filter
        </Typography>
        <Typography variant="body2" paragraph>
          Quick category filtering with responsive chip layout. Extra categories move to a "more" menu on mobile.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <CategoryFilter
          activeCategory={activeCategory}
          onCategoryChange={setActiveCategory}
          categories={categories}
          label="Filter by Category"
        />
        
        <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="body2">
            Active Category: <strong>{activeCategory}</strong>
          </Typography>
        </Box>
      </Paper>
      
      {/* Combined Example */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Combined Example
        </Typography>
        <Typography variant="body2" paragraph>
          All components working together in a typical learning tools page layout.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <Box sx={{ mb: 3 }}>
          <SearchTools
            onSearch={handleSearch}
            onResultClick={handleSearchResultClick}
            loading={searchLoading}
            results={searchResults}
          />
        </Box>
        
        <CategoryFilter
          activeCategory={activeCategory}
          onCategoryChange={setActiveCategory}
          categories={categories}
        />
        
        <FilterBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          filters={filters}
          onFilterChange={setFilters}
          availableFilters={availableFilters}
          sortBy={sortBy}
          sortDirection={sortDirection}
          onSortChange={handleSortChange}
          availableSorts={availableSorts}
        />
        
        <Box sx={{ p: 3, bgcolor: 'background.default', borderRadius: 1, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            Filtered content would appear here based on the selected filters and search criteria.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default NavigationDemo;