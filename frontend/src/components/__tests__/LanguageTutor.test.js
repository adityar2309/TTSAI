import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import LanguageTutor from '../LanguageTutor';

const theme = createTheme();

const mockExplanation = {
  meaning: "This is a test meaning with detailed explanation",
  examples: [
    {
      sentence: "Test sentence in target language",
      translation: "Test sentence in English"
    },
    {
      sentence: "Another example sentence",
      translation: "Another example in English"
    }
  ],
  grammar_tip: "This is a grammar tip for the phrase",
  cultural_insight: "This is cultural context about the phrase"
};

const renderWithTheme = (component) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('LanguageTutor Component', () => {
  test('renders with complete explanation data', () => {
    renderWithTheme(<LanguageTutor explanation={mockExplanation} />);
    
    // Check header
    expect(screen.getByText('Language Tutor')).toBeInTheDocument();
    
    // Check all sections are present
    expect(screen.getByText('Meaning & Nuances')).toBeInTheDocument();
    expect(screen.getByText('Example Sentences')).toBeInTheDocument();
    expect(screen.getByText('Grammar Tip')).toBeInTheDocument();
    expect(screen.getByText('Cultural Insight')).toBeInTheDocument();
    
    // Check content
    expect(screen.getByText(mockExplanation.meaning)).toBeInTheDocument();
    expect(screen.getByText(mockExplanation.grammar_tip)).toBeInTheDocument();
    expect(screen.getByText(mockExplanation.cultural_insight)).toBeInTheDocument();
    
    // Check examples
    expect(screen.getByText('"Test sentence in target language"')).toBeInTheDocument();
    expect(screen.getByText('Test sentence in English')).toBeInTheDocument();
  });

  test('handles missing explanation gracefully', () => {
    renderWithTheme(<LanguageTutor explanation={null} />);
    
    // Component should not render anything when explanation is null
    expect(screen.queryByText('Language Tutor')).not.toBeInTheDocument();
  });

  test('handles partial explanation data', () => {
    const partialExplanation = {
      meaning: "Only meaning provided",
      examples: []
    };
    
    renderWithTheme(<LanguageTutor explanation={partialExplanation} />);
    
    // Should render header and meaning
    expect(screen.getByText('Language Tutor')).toBeInTheDocument();
    expect(screen.getByText('Meaning & Nuances')).toBeInTheDocument();
    expect(screen.getByText('Only meaning provided')).toBeInTheDocument();
    
    // Should not render sections without data
    expect(screen.queryByText('Example Sentences')).not.toBeInTheDocument();
    expect(screen.queryByText('Grammar Tip')).not.toBeInTheDocument();
    expect(screen.queryByText('Cultural Insight')).not.toBeInTheDocument();
  });

  test('handles string examples (backward compatibility)', () => {
    const explanationWithStringExamples = {
      meaning: "Test meaning",
      examples: ["Simple string example", "Another string example"]
    };
    
    renderWithTheme(<LanguageTutor explanation={explanationWithStringExamples} />);
    
    expect(screen.getByText('Example Sentences')).toBeInTheDocument();
    expect(screen.getByText('"Simple string example"')).toBeInTheDocument();
    expect(screen.getByText('"Another string example"')).toBeInTheDocument();
  });

  test('displays appropriate icons for each section', () => {
    renderWithTheme(<LanguageTutor explanation={mockExplanation} />);
    
    // Check that the section labels are present (which indicates chips are rendered)
    expect(screen.getByText('Meaning & Nuances')).toBeInTheDocument();
    expect(screen.getByText('Example Sentences')).toBeInTheDocument();
    expect(screen.getByText('Grammar Tip')).toBeInTheDocument();
    expect(screen.getByText('Cultural Insight')).toBeInTheDocument();
    
    // Check that icons are present by their test IDs
    expect(screen.getByTestId('BookIcon')).toBeInTheDocument();
    expect(screen.getByTestId('ChatIcon')).toBeInTheDocument();
    expect(screen.getByTestId('PsychologyIcon')).toBeInTheDocument();
    expect(screen.getByTestId('PublicIcon')).toBeInTheDocument();
  });
});