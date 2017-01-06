const exec = require('child_process').execSync;
const fs = require('fs');

var minus = "-";
var plus = "+";
var outBuff = [];
const depth = 20;
for (let i = 1; i < depth; i++) {
  for (let j = 1; j < depth; j++) {
    for (let k = 1; k < depth; k++) {
      let line = `${minus.repeat(i)}[${minus.repeat(j)}>${plus.repeat(k)}<]>[-<+>]<`;
      let res = exec(`node bf.js --cycle 20000 -e=\"${line}$\"`);
      if (res.length !== 0) {
        outBuff.push([line, res.toString()]);
      }
    }
  }
}
outBuff.sort(function(a, b) {
  if (a[0].length < b[0].length) {
    return -1;
  }
  if (a[0].length > b[0].length) {
    return 1;
  }
  return 0;
});
for (let k = 0; k < 30; k++) {
  for (let i = 0; i < depth; i++) {
    let line = `${outBuff[k][0]}${plus.repeat(i)}`;
    let res = exec(`node bf.js --cycle 20000 -e=\"${line}$\"`);
    if (res.length !== 0) {
      outBuff.push([line, res.toString()]);
    }
    line = `${outBuff[k][0]}${minus.repeat(i)}`;
    res = exec(`node bf.js --cycle 20000 -e=\"${line}$\"`);
    if (res.length !== 0) {
      outBuff.push([line, res.toString()]);
    }
  }
}
for (let i = 0; i < depth; i++) {
  let line = `${plus.repeat(i)}`;
  let res = exec(`node bf.js --cycle 20000 -e=\"${line}$\"`);
  if (res.length !== 0) {
    outBuff.push([line, res.toString()]);
  }
  line = `${minus.repeat(i)}`;
  res = exec(`node bf.js --cycle 20000 -e=\"${line}$\"`);
  if (res.length !== 0) {
    outBuff.push([line, res.toString()]);
  }
}

var optimized = {};
outBuff.forEach(function(item) {
  if (!optimized[item[1]]) {
    optimized[item[1]] = item[0];
  } else {
    if (optimized[item[1]].length > item[0].length) {
      optimized[item[1]] = item[0];
    }
  }
});
console.log(optimized);
fs.writeFile('out.json', JSON.stringify(optimized));
