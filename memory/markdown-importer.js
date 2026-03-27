'use strict';

/**
 * Markdown Importer - Parses memory Markdown files into structured objects
 *
 * Handles:
 * - insights.md: Decisoes (table), Padroes (table), Armadilhas (table), Notas de Sessao (sections)
 * - progresso.md: Estado geral, work done, next steps
 * - roadmaps/*.md: Multi-phase roadmaps with checkboxes
 */

const fs = require('fs');
const path = require('path');

/**
 * Parse a Markdown table into array of objects
 * @param {string} text - Table text including header
 * @returns {object[]}
 */
function parseMarkdownTable(text) {
  const lines = text.trim().split('\n').filter((l) => l.trim());
  if (lines.length < 3) return [];

  const headers = lines[0]
    .split('|')
    .map((h) => h.trim())
    .filter(Boolean);

  const rows = [];
  for (let i = 2; i < lines.length; i++) {
    const cells = lines[i]
      .split('|')
      .map((c) => c.trim())
      .filter(Boolean);
    if (cells.length >= headers.length) {
      const row = {};
      headers.forEach((h, idx) => {
        row[h.toLowerCase().replace(/\s+/g, '_')] = cells[idx] || '';
      });
      rows.push(row);
    }
  }

  return rows;
}

/**
 * Extract sections from Markdown (## and ### headings)
 * @param {string} text
 * @returns {object[]} Array of {heading, level, content}
 */
function extractSections(text) {
  const sections = [];
  const lines = text.split('\n');
  let currentHeading = null;
  let currentLevel = 0;
  let currentContent = [];

  for (const line of lines) {
    const headingMatch = line.match(/^(#{2,3})\s+(.+)/);
    if (headingMatch) {
      if (currentHeading) {
        sections.push({
          heading: currentHeading,
          level: currentLevel,
          content: currentContent.join('\n').trim(),
        });
      }
      currentHeading = headingMatch[2].trim();
      currentLevel = headingMatch[1].length;
      currentContent = [];
    } else {
      currentContent.push(line);
    }
  }

  if (currentHeading) {
    sections.push({
      heading: currentHeading,
      level: currentLevel,
      content: currentContent.join('\n').trim(),
    });
  }

  return sections;
}

/**
 * Parse insights.md into memory items
 * @param {string} filePath
 * @returns {object[]}
 */
function parseInsights(filePath) {
  const text = fs.readFileSync(filePath, 'utf-8');
  const sections = extractSections(text);
  const items = [];

  for (const section of sections) {
    if (section.heading.match(/decisoe?s/i)) {
      const rows = parseMarkdownTable(section.content);
      for (const row of rows) {
        items.push({
          memory_type: 'decision',
          title: row.decisao || row.decisão || Object.values(row)[1] || 'Decision',
          content: `Data: ${row.data || ''}. Contexto: ${row.contexto || ''}. Alternativas descartadas: ${row.alternativas_descartadas || ''}`,
          importance: 'high',
          tags: ['decision'],
          source: 'import',
          source_file: filePath,
        });
      }
    } else if (section.heading.match(/padr[oõ]es/i)) {
      const rows = parseMarkdownTable(section.content);
      for (const row of rows) {
        items.push({
          memory_type: 'pattern',
          title: row.padrao || row.padrão || Object.values(row)[0] || 'Pattern',
          content: `Onde aparece: ${row.onde_aparece || ''}. Exemplo: ${row.exemplo || ''}`,
          importance: 'normal',
          tags: ['pattern'],
          source: 'import',
          source_file: filePath,
        });
      }
    } else if (section.heading.match(/armadilhas|gotchas/i)) {
      const rows = parseMarkdownTable(section.content);
      for (const row of rows) {
        items.push({
          memory_type: 'gotcha',
          title: row.armadilha || Object.values(row)[0] || 'Gotcha',
          content: `Impacto: ${row.impacto || ''}. Como evitar: ${row.como_evitar || ''}`,
          importance: 'high',
          tags: ['gotcha'],
          source: 'import',
          source_file: filePath,
        });
      }
    } else if (section.heading.match(/notas?\s+de\s+sess[aã]o/i) || section.heading.match(/\d{4}-\d{2}-\d{2}/)) {
      if (section.content.length > 10) {
        items.push({
          memory_type: 'session_note',
          title: section.heading,
          content: section.content,
          importance: 'normal',
          tags: ['session'],
          source: 'import',
          source_file: filePath,
        });
      }
    }
  }

  return items;
}

/**
 * Parse progresso.md into memory items
 * @param {string} filePath
 * @returns {object[]}
 */
function parseProgresso(filePath) {
  const text = fs.readFileSync(filePath, 'utf-8');
  const sections = extractSections(text);
  const items = [];

  for (const section of sections) {
    if (section.content.length < 10) continue;

    let memType = 'progress';
    let importance = 'normal';
    const tags = ['progress'];

    if (section.heading.match(/proximo\s+passo|next/i)) {
      importance = 'high';
      tags.push('next-step');
    } else if (section.heading.match(/n[aã]o\s+testado|untested/i)) {
      importance = 'high';
      tags.push('untested');
    } else if (section.heading.match(/contexto/i)) {
      tags.push('context');
    }

    items.push({
      memory_type: memType,
      title: `Progresso: ${section.heading}`,
      content: section.content,
      importance,
      tags,
      source: 'import',
      source_file: filePath,
      expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    });
  }

  return items;
}

/**
 * Parse a roadmap file into a memory item
 * @param {string} filePath
 * @returns {object[]}
 */
function parseRoadmap(filePath) {
  const text = fs.readFileSync(filePath, 'utf-8');
  const basename = path.basename(filePath, '.md');

  const totalCheckboxes = (text.match(/\[[ x]\]/g) || []).length;
  const completedCheckboxes = (text.match(/\[x\]/gi) || []).length;

  return [{
    memory_type: 'roadmap',
    title: `Roadmap: ${basename}`,
    content: text,
    importance: 'normal',
    tags: ['roadmap', basename],
    source: 'import',
    source_file: filePath,
    metadata: {
      total_items: totalCheckboxes,
      completed_items: completedCheckboxes,
      progress_pct: totalCheckboxes > 0 ? Math.round((completedCheckboxes / totalCheckboxes) * 100) : 0,
    },
  }];
}

/**
 * Parse a single Markdown file (auto-detect type)
 * @param {string} filePath
 * @returns {object[]}
 */
function parseMarkdownFile(filePath) {
  const basename = path.basename(filePath).toLowerCase();

  if (basename === 'insights.md') return parseInsights(filePath);
  if (basename === 'progresso.md') return parseProgresso(filePath);
  if (basename.endsWith('.md')) return parseRoadmap(filePath);

  return [];
}

/**
 * Parse all memory files from the memoria/ directory
 * @param {string} memoriaDir
 * @returns {object[]}
 */
function parseAllMemoryFiles(memoriaDir) {
  const items = [];

  const insightsPath = path.join(memoriaDir, 'insights.md');
  if (fs.existsSync(insightsPath)) {
    items.push(...parseInsights(insightsPath));
  }

  const progressoPath = path.join(memoriaDir, 'progresso.md');
  if (fs.existsSync(progressoPath)) {
    items.push(...parseProgresso(progressoPath));
  }

  const roadmapsDir = path.join(memoriaDir, 'roadmaps');
  if (fs.existsSync(roadmapsDir)) {
    const roadmapFiles = fs.readdirSync(roadmapsDir).filter((f) => f.endsWith('.md'));
    for (const file of roadmapFiles) {
      items.push(...parseRoadmap(path.join(roadmapsDir, file)));
    }
  }

  return items;
}

module.exports = {
  parseMarkdownFile,
  parseAllMemoryFiles,
  parseInsights,
  parseProgresso,
  parseRoadmap,
  parseMarkdownTable,
  extractSections,
};
