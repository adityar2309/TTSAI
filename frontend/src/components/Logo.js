import React from 'react';
import { Box, Typography } from '@mui/material';
import { Link } from 'react-router-dom';
import TranslateIcon from '@mui/icons-material/Translate';

const Logo = () => {
  return (
    <Box
      component={Link}
      to="/"
      sx={{
        display: 'flex',
        alignItems: 'center',
        textDecoration: 'none',
        color: 'primary.main',
        '&:hover': {
          opacity: 0.8,
        },
      }}
    >
      <TranslateIcon 
        sx={{ 
          fontSize: 32,
          mr: 1,
          transform: 'rotate(-10deg)',
        }} 
      />
      <Typography
        variant="h4"
        component="span"
        sx={{
          fontWeight: 700,
          letterSpacing: 1,
          background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}
      >
        TTSAI
      </Typography>
    </Box>
  );
};

export default Logo; 