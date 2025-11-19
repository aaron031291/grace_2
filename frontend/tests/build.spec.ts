/**
 * Build Validation Tests
 * 
 * Ensures build output is valid and contains expected files
 */

import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const DIST_PATH = path.join(process.cwd(), 'dist');

test.describe('Build Validation', () => {
  
  test.beforeAll(() => {
    // Ensure build has been run
    if (!fs.existsSync(DIST_PATH)) {
      throw new Error('Dist folder not found. Run "npm run build" first.');
    }
  });
  
  test('dist folder exists and contains files', () => {
    expect(fs.existsSync(DIST_PATH)).toBeTruthy();
    
    const files = fs.readdirSync(DIST_PATH);
    expect(files.length).toBeGreaterThan(0);
  });
  
  test('index.html exists and is valid', () => {
    const indexPath = path.join(DIST_PATH, 'index.html');
    expect(fs.existsSync(indexPath)).toBeTruthy();
    
    const content = fs.readFileSync(indexPath, 'utf-8');
    
    // Should have HTML structure
    expect(content).toContain('<!DOCTYPE html>');
    expect(content).toContain('<html');
    expect(content).toContain('</html>');
    
    // Should reference assets
    expect(content).toMatch(/<script.*type="module"/);
  });
  
  test('assets folder contains JavaScript bundles', () => {
    const assetsPath = path.join(DIST_PATH, 'assets');
    
    if (fs.existsSync(assetsPath)) {
      const files = fs.readdirSync(assetsPath);
      const jsFiles = files.filter(f => f.endsWith('.js'));
      
      expect(jsFiles.length).toBeGreaterThan(0);
    }
  });
  
  test('assets folder contains CSS bundles', () => {
    const assetsPath = path.join(DIST_PATH, 'assets');
    
    if (fs.existsSync(assetsPath)) {
      const files = fs.readdirSync(assetsPath);
      const cssFiles = files.filter(f => f.endsWith('.css'));
      
      expect(cssFiles.length).toBeGreaterThan(0);
    }
  });
  
  test('no TypeScript files in dist', () => {
    const assetsPath = path.join(DIST_PATH, 'assets');
    
    if (fs.existsSync(assetsPath)) {
      const files = fs.readdirSync(assetsPath);
      const tsFiles = files.filter(f => f.endsWith('.ts') || f.endsWith('.tsx'));
      
      expect(tsFiles.length).toBe(0);
    }
  });
  
  test('bundle size is reasonable', () => {
    const assetsPath = path.join(DIST_PATH, 'assets');
    
    if (fs.existsSync(assetsPath)) {
      const files = fs.readdirSync(assetsPath);
      const jsFiles = files.filter(f => f.endsWith('.js'));
      
      // Check main bundle isn't too large (< 5MB)
      for (const file of jsFiles) {
        const filePath = path.join(assetsPath, file);
        const stats = fs.statSync(filePath);
        const sizeInMB = stats.size / (1024 * 1024);
        
        expect(sizeInMB).toBeLessThan(5);
      }
    }
  });
  
});
