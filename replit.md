# Overview

A German quiz application built with Streamlit that allows users to practice questions from a structured question pool. The application supports loading questions from local directories or uploaded ZIP files and provides interactive quiz sessions with answer validation and progress tracking.

# User Preferences

Preferred communication style: Simple, everyday language.

# Recent Changes

## August 19, 2025
- Converted command-line Python quiz application to web-based Streamlit platform
- Created comprehensive question database with 260+ questions across 10 topics:
  - Grundlagen der Pflege (30 questions with authentic answers and synonyms)
  - Medikamentenlehre (10 questions)
  - Rechtskunde (10 questions)  
  - Erste Hilfe Maßnahmen (30 questions with authentic emergency response procedures)
  - Pflegemodelle und Technik (30 questions covering nursing theories and advanced techniques)
  - Pflegeplanung und Pflegedokumentation (30 questions on systematic care planning and documentation)
  - Ethik in der Pflege (30 questions covering moral principles and ethical decision-making in healthcare)
  - Krankheitslehre und Alterskrankheiten (30 questions on diseases and age-related health conditions)
  - Präoperative/Postoperative Maßnahmen (30 questions on surgical care procedures)
  - Ernährung (30 questions on nutrition and dietary management in healthcare)
- Implemented intelligent answer validation using synonym matching
- Added file upload functionality for ZIP-based question sets
- **Enhanced with multilingual support**: Full German and Turkish language interface based on original CLI program design
- **Advanced result analysis**: Detailed quiz performance analytics with weak topic identification
- **Improved user experience**: Streamlined navigation, progress tracking, and responsive design
- **Extended navigation features**: Added topic overview navigation, back functionality, and main page access during quiz sessions
- **Enhanced topic selection**: Visual topic overview with direct start buttons and question counts
- System now fully operational with learning and exam simulation modes matching original CLI functionality

# System Architecture

## Frontend Architecture
- **Streamlit-based Web Interface**: Single-page application using Streamlit for the user interface, providing a simple and interactive web-based experience
- **Session State Management**: Utilizes Streamlit's session state to maintain quiz progress, question data, and application mode across user interactions
- **File Upload Interface**: Built-in file upload component for ZIP files containing question sets

## Backend Architecture
- **Modular Python Design**: Separated into three main modules:
  - `app.py`: Main application controller and UI logic
  - `file_handler.py`: File system operations and question loading
  - `quiz_logic.py`: Quiz session management and answer validation
- **Object-Oriented Quiz Management**: `QuizSession` class handles quiz state, progress tracking, and answer evaluation
- **Intelligent Path Resolution**: Dynamic path detection that works with both development (.py) and compiled (.exe) environments

## Data Storage Solutions
- **File-based Question Storage**: Questions stored in structured text files within a `pflegepool` directory hierarchy
- **Temporary File Handling**: Automatic cleanup of temporary directories created during ZIP file extraction
- **In-Memory Session Data**: Quiz progress and answers stored in Streamlit session state for the duration of the session

## Question Data Structure
- **Hierarchical Organization**: Questions organized by topics in separate directories
- **Multi-file Format**: Each topic contains:
  - `fragen.txt`: Question text
  - `antworten.txt`: Correct answers
  - `synonyme.txt`: Alternative acceptable answers (optional)
- **UTF-8 Encoding**: Full Unicode support for German language content

## Answer Validation System
- **Flexible Matching**: Supports exact matches and synonym-based validation
- **Case-insensitive Comparison**: Answers validated regardless of capitalization
- **Progress Tracking**: Maintains history of correct/incorrect answers and overall quiz statistics

# External Dependencies

## Core Framework
- **Streamlit**: Web application framework providing the user interface and session management capabilities

## Standard Library Dependencies
- **os**: File system operations and path management
- **zipfile**: ZIP file extraction for uploaded question sets
- **tempfile**: Temporary directory creation for file processing
- **shutil**: Directory cleanup operations
- **random**: Question shuffling functionality
- **sys**: Executable path detection for compiled applications

## File System Requirements
- **Local Directory Structure**: Expects `pflegepool` directory with topic subdirectories containing question files
- **ZIP Upload Support**: Ability to extract and process uploaded ZIP files with the same directory structure