import tsParser from '@typescript-eslint/parser';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import sonarjsPlugin from 'eslint-plugin-sonarjs';

export default [
  {
    ignores: ['node_modules/**', '.next/**', 'coverage/**', '.scripts-out/**'],
  },
  {
    files: ['src/**/*.ts', 'src/**/*.tsx', 'tests/**/*.ts'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        project: './tsconfig.json',
      },
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      sonarjs: sonarjsPlugin,
    },
    rules: {
      // @typescript-eslint v8 recommended rules (flat config)
      ...(tsPlugin.configs['recommended']?.[1]?.rules ?? {}),
      // sonarjs recommended rules
      ...(sonarjsPlugin.configs?.recommended?.rules ?? {}),
      'sonarjs/cognitive-complexity': ['error', 10],
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },
];
