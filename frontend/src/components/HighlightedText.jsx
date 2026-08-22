import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const HighlightedText = ({ text, highlights }) => {
  const [activeTooltip, setActiveTooltip] = useState(null);

  if (!highlights || highlights.length === 0) {
    return <p className="text-gray-700 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">{text}</p>;
  }

  // Sort highlights by starting index to avoid overlap issues
  // But wait, the backend just gives the string text that matches.
  // We need to replace these substrings with highlighted spans.
  
  let processedText = [];
  let currentIdx = 0;
  
  // A naive approach for highlighting since backend only gives text strings.
  // We will find occurrences of the highlighted text and wrap them.
  // For better accuracy, the backend should return start/end offsets, but for now we'll do simple replace.
  
  // Let's create an array of matches.
  const matches = [];
  highlights.forEach(h => {
    const idx = text.toLowerCase().indexOf(h.text.toLowerCase());
    if (idx !== -1) {
      matches.push({
        start: idx,
        end: idx + h.text.length,
        original: text.substring(idx, idx + h.text.length),
        ...h
      });
    }
  });

  // Sort matches by start index
  matches.sort((a, b) => a.start - b.start);

  // Filter overlapping matches
  const validMatches = [];
  let lastEnd = 0;
  for (const match of matches) {
    if (match.start >= lastEnd) {
      validMatches.push(match);
      lastEnd = match.end;
    }
  }

  let lastIndex = 0;
  const elements = [];

  validMatches.forEach((match, i) => {
    // Add text before match
    if (match.start > lastIndex) {
      elements.push(
        <span key={`text-${i}`}>{text.substring(lastIndex, match.start)}</span>
      );
    }
    
    // Determine color based on type
    let colorClass = "bg-yellow-200 dark:bg-yellow-800/50 text-yellow-900 dark:text-yellow-100";
    if (match.type === 'urgency') colorClass = "bg-orange-200 dark:bg-orange-800/50 text-orange-900 dark:text-orange-100 border-b-2 border-orange-500";
    if (match.type === 'financial') colorClass = "bg-green-200 dark:bg-green-800/50 text-green-900 dark:text-green-100 border-b-2 border-green-500";
    if (match.type === 'credential') colorClass = "bg-red-200 dark:bg-red-800/50 text-red-900 dark:text-red-100 border-b-2 border-red-500";
    if (match.type === 'url') colorClass = "bg-blue-200 dark:bg-blue-800/50 text-blue-900 dark:text-blue-100 border-b-2 border-blue-500";
    if (match.type === 'impersonation') colorClass = "bg-purple-200 dark:bg-purple-800/50 text-purple-900 dark:text-purple-100 border-b-2 border-purple-500";

    elements.push(
      <span 
        key={`match-${i}`} 
        className={`relative inline-block cursor-pointer font-medium px-1 rounded-sm ${colorClass} transition-colors duration-200 hover:brightness-110`}
        onMouseEnter={() => setActiveTooltip(i)}
        onMouseLeave={() => setActiveTooltip(null)}
      >
        {match.original}
        <AnimatePresence>
          {activeTooltip === i && (
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: -5 }}
              exit={{ opacity: 0, y: 0 }}
              className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 text-xs text-white bg-gray-900 rounded shadow-lg z-10 pointer-events-none"
            >
              <div className="font-bold mb-1 uppercase tracking-wider text-[10px] text-gray-400">{match.type}</div>
              {match.reason}
              {/* Tooltip arrow */}
              <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
            </motion.div>
          )}
        </AnimatePresence>
      </span>
    );
    lastIndex = match.end;
  });

  // Add remaining text
  if (lastIndex < text.length) {
    elements.push(<span key={`text-end`}>{text.substring(lastIndex)}</span>);
  }

  return (
    <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-100 dark:border-gray-700 leading-loose text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
      {elements.length > 0 ? elements : text}
    </div>
  );
};

export default HighlightedText;
