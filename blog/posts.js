/**
 * Blog post registry — Thomas Pasley
 *
 * To add a new post:
 *   1. Create blog/posts/<slug>.html
 *   2. Add an entry here (newest first).
 */
const BLOG_POSTS = [
    {
        slug: 'feature-engineering-financial-time-series',
        title: 'Feature Engineering for Financial Time-Series',
        description: 'A practical walkthrough of building meaningful features from raw OHLCV data — lag features, rolling statistics, and technical indicators that actually improve model performance.',
        date: '2026-06-05',
        readTime: 8,
        tags: ['Python', 'Machine Learning', 'Feature Engineering', 'Finance'],
        featured: true
    }
];
