# Job-Hunting-AI-Web-Tool

A team capstone project that uses semantic search and AI embeddings to match user resumes with relevant job postings

## Project Overview

Users can upload a resume and receive ranked job reccomendations based on semantic similarity between resume content and job descriptions

## My Contributions

I was responsible for the AI and data pipeline components of the project, including:

- Researching and integrating Google Gemini embedding models
- Building the automated job ingestion pipeline using Greenhouse APIs
- Processing and cleaning job posting data
- Generating vector embeddings for resumes and job descriptions
- Designing and implementing semantic similarity ranking
- Integrating pgvector-based similarity search
- Creating recommendation endpoints that return ranked job matches
- Implementing resume embedding storage and retrieval through Supabase

## Technologies Used

- Python
- Flask
- PostgreSQL
- pgvector
- Supabase
- Google Gemini Embeddings API
- Greenhouse Job Board API
- JWT Authentication
- BeautifulSoup

## Files Included In This Repository

This repository contains components that I personally developed for the project.

## Key Features

### Job Ingestion Pipeline

Retrieves job postings from Greenhouse-hosted job boards, cleans job descriptions, and stores structured job data for downstream processing.

### Vector Embeddings

Generates 768-dimensional embeddings using Google's Gemini embedding model for both resumes and job descriptions.

### Semantic Job Matching
Uses pgvector similarity search to compare resume embeddings against job embeddings.

### Recommendation Engine

Ranks jobs according to semantic similarity and returns the most relevant opportunities to the user.

## Project Scale

- Over 5,000 job postings processed
- 768-dimensional vector embeddings
- Automated ingestion from multiple Greenhouse companies
- Semantic search powered by pgvector similarity matching

## Screenshots
