/**
 * This scripts run the main program but converts CLI output to html formated string keeping colors
 */

const readline = require("readline");
const Convert = require("ansi-to-html");
const child_process = require("child_process");
const path = require("path");

const convert = new Convert({ bg: "black", newline: true, escapeXML: true });

const args = process.argv.slice(2);
const exePath = path.join(__dirname, "..", ".env", "bin", "python");
const programPath = path.join(__dirname, "..", "main.py");

const p = child_process.spawn(exePath, [programPath, ...args], {
  env: {
    ...process.env,
    FORCE_COLOR: 1,
  },
});

var rl = readline.createInterface({
  input: p.stdout,
  output: process.stdout,
  terminal: false,
});

console.log(
  '<pre style="background:#343a40; width: fit-content; color: white;">'
);
rl.on("line", (line) => {
  const str = convert.toHtml(line);
  console.log(str);
}).on("close", () => {
  console.log("</pre>");
  process.exit(0);
});
