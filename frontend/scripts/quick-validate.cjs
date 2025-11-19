#!/usr/bin/env node
/**
 * Quick Build Validation Script
 * Checks build output without requiring playwright
 */

const fs = require('fs');
const path = require('path');

const DIST_PATH = path.join(__dirname, '..', 'dist');
const SRC_PATH = path.join(__dirname, '..', 'src');

let errors = 0;
let warnings = 0;

function log(symbol, message) {
  console.log(`${symbol} ${message}`);
}

function error(message) {
  log('[ERROR]', message);
  errors++;
}

function warn(message) {
  log('[WARN]', message);
  warnings++;
}

function success(message) {
  log('[OK]', message);
}

console.log('Frontend Build Validation\n');

// Check 1: Dist folder exists
if (!fs.existsSync(DIST_PATH)) {
  error('dist/ folder not found. Run "npm run build" first.');
} else {
  success('dist/ folder exists');
  
  // Check 2: index.html exists
  const indexPath = path.join(DIST_PATH, 'index.html');
  if (!fs.existsSync(indexPath)) {
    error('dist/index.html not found');
  } else {
    success('dist/index.html exists');
    
    // Check 3: index.html is valid
    const indexContent = fs.readFileSync(indexPath, 'utf-8');
    if (!indexContent.includes('<!DOCTYPE html>')) {
      error('index.html missing DOCTYPE');
    } else if (!indexContent.includes('</html>')) {
      error('index.html incomplete');
    } else {
      success('dist/index.html is valid HTML');
    }
  }
  
  // Check 4: Assets folder
  const assetsPath = path.join(DIST_PATH, 'assets');
  if (fs.existsSync(assetsPath)) {
    const files = fs.readdirSync(assetsPath);
    const jsFiles = files.filter(f => f.endsWith('.js'));
    const cssFiles = files.filter(f => f.endsWith('.css'));
    
    if (jsFiles.length === 0) {
      error('No JavaScript bundles found in dist/assets');
    } else {
      success(`${jsFiles.length} JavaScript bundle(s) found`);
    }
    
    if (cssFiles.length === 0) {
      warn('No CSS bundles found in dist/assets');
    } else {
      success(`${cssFiles.length} CSS bundle(s) found`);
    }
    
    // Check bundle sizes
    jsFiles.forEach(file => {
      const filePath = path.join(assetsPath, file);
      const stats = fs.statSync(filePath);
      const sizeInMB = (stats.size / (1024 * 1024)).toFixed(2);
      
      if (stats.size > 5 * 1024 * 1024) {
        warn(`Large bundle: ${file} (${sizeInMB} MB)`);
      } else {
        success(`Bundle size OK: ${file} (${sizeInMB} MB)`);
      }
    });
  }
}

// Check 5: No legacy files in src root
console.log('');
const srcFiles = fs.readdirSync(SRC_PATH);
const legacyPatterns = [
  'GraceAgentic.tsx',
  'GraceChat.tsx',
  'GraceChatGPT.tsx',
  'GraceClean.tsx',
  'App.backup.tsx',
  'App.minimal.tsx'
];

let foundLegacy = false;
legacyPatterns.forEach(pattern => {
  if (srcFiles.includes(pattern)) {
    error(`Legacy file in src root: ${pattern} (should be in src/legacy/)`);
    foundLegacy = true;
  }
});

if (!foundLegacy) {
  success('No legacy files in src root');
}

// Check 6: Legacy folder exists
if (!srcFiles.includes('legacy')) {
  warn('src/legacy/ folder not found');
} else {
  success('src/legacy/ folder exists');
}

// Summary
console.log('\n' + '='.repeat(50));
if (errors > 0) {
  console.log(`[FAILED] ${errors} error(s), ${warnings} warning(s)`);
  process.exit(1);
} else if (warnings > 0) {
  console.log(`[WARNING] 0 errors, ${warnings} warning(s)`);
  process.exit(0);
} else {
  console.log('[SUCCESS] All validation checks passed!');
  process.exit(0);
}
