const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const projectDir = 'D:/budget/app';
const jdkPath = '/tmp/jdk17_extracted/jdk-17.0.12+7';

// Clean previous
if (fs.existsSync(projectDir)) fs.rmSync(projectDir, { recursive: true });

// Run bubblewrap init with answers piped
const input = `n\n${jdkPath}\nn\nn\nn\n`;
execSync(`npx @bubblewrap/cli init --manifest=https://emdjj.github.io/budget/manifest.json`, {
  cwd: 'D:/budget',
  input,
  stdio: ['pipe', 'inherit', 'inherit'],
  env: { ...process.env, PATH: `${jdkPath}/bin:${process.env.PATH}` }
});
