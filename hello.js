const fs = require('fs');

const list = (basePath) => {
  try {
    const files = fs.readdirSync(basePath);
    const folders = files.filter(f => fs.statSync(`${basePath}/${f}`).isDirectory());
    const filesOnly = files.filter(f => !fs.statSync(`${basePath}/${f}`).isDirectory());
    return {
      files: filesOnly,
      folders
    };
  } catch (err) {
    throw new Error(`Error accessing path ${basePath}: ${err.message}`);
  }
};
