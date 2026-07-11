import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'OpenRecall Docs',
  tagline: 'Static, country-extensible medicine recall search',
  url: 'https://mrueda.github.io',
  baseUrl: '/openrecall/',
  organizationName: 'mrueda',
  projectName: 'openrecall',
  onBrokenLinks: 'warn',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: 'docs',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],
  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        language: ['en'],
        indexDocs: true,
        indexBlog: false,
        docsRouteBasePath: '/docs',
      },
    ],
  ],
  themeConfig: {
    image: 'img/openrecall-social.svg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'OpenRecall',
      logo: {
        alt: 'OpenRecall logo',
        src: 'img/openrecall-logo.svg',
      },
      items: [
        {
          to: '/app',
          label: 'Live Search',
          position: 'left',
        },
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/docs/usage/quickstart',
          label: 'Quick Start',
          position: 'left',
        },
        {
          to: '/docs/technical-details/data-schema',
          label: 'Data Schema',
          position: 'left',
        },
        {
          href: 'https://github.com/mrueda/openrecall',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Overview',
              to: '/docs/overview',
            },
            {
              label: 'Quick Start',
              to: '/docs/usage/quickstart',
            },
            {
              label: 'Operations',
              to: '/docs/usage/operations',
            },
            {
              label: 'AEMPS Collector',
              to: '/docs/technical-details/aemps-collector',
            },
            {
              label: 'CLI Reference',
              to: '/docs/reference/cli',
            },
          ],
        },
        {
          title: 'Project',
          items: [
            {
              label: 'Repository',
              href: 'https://github.com/mrueda/openrecall',
            },
            {
              label: 'License',
              href: 'https://github.com/mrueda/openrecall/blob/main/LICENSE',
            },
          ],
        },
      ],
      copyright: 'Copyright (C) 2026 Manuel Rueda.',
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
