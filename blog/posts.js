/**
 * Blog post registry — Thomas Pasley
 *
 * To add a new post:
 *   1. Create blog/posts/<slug>.html
 *   2. Add an entry here (newest first).
 */
const BLOG_POSTS = [
    {
        slug: 'week1-survivorship-bias',
        title: 'Week 1: Survivorship Bias and the Hidden Cost of Dirty Data',
        description: 'The single most common reason backtests look better than live trading — and how to measure the damage. We build two portfolios, compare the results, and are honest about what the simulation can and cannot tell us.',
        date: '2026-06-07',
        readTime: 10,
        tags: ['Quantitative Finance', 'Data Quality', 'Backtesting', 'Python'],
        featured: true
    }
];
