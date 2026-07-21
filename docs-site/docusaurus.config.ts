import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const isProduction = process.env.NODE_ENV === 'production';

const config: Config = {
  title: 'RecallRx Docs',
  tagline: 'Static, country-extensible medicine recall search',
  url: 'https://mrueda.github.io',
  baseUrl: '/recallrx/',
  favicon: 'img/recallrx-logo.svg',
  organizationName: 'mrueda',
  projectName: 'recallrx',
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
  themes: isProduction
    ? [
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
      ]
    : [],
  themeConfig: {
    image: 'img/recallrx-social.png',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'RecallRx',
      logo: {
        alt: 'RecallRx logo',
        src: 'img/recallrx-logo.svg',
      },
      items: [
        {
          href: 'https://mrueda.github.io/recallrx/app/',
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
          label: 'User Guide',
          position: 'left',
        },
        {
          href: 'https://github.com/mrueda/recallrx',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'For Users',
          items: [
            {
              label: 'Live Search',
              href: 'https://mrueda.github.io/recallrx/app/',
            },
            {
              label: 'Use the App',
              to: '/docs/usage/quickstart',
            },
            {
              label: 'Safety Language',
              to: '/docs/usage/safety-language',
            },
          ],
        },
        {
          title: 'For Developers',
          items: [
            {
              label: 'Architecture',
              to: '/docs/technical-details/architecture',
            },
            {
              label: 'Source Adapters',
              to: '/docs/technical-details/source-adapters',
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
              href: 'https://github.com/mrueda/recallrx',
            },
            {
              label: 'License',
              href: 'https://github.com/mrueda/recallrx/blob/main/LICENSE',
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
