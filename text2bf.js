#!/usr/bin/env node

const assert = require('assert');
const fs = require('fs');
const numbers = JSON.parse(fs.readFileSync('numbers.json', 'utf8'));
const argv = require('minimist')(process.argv.slice(2));
const combinations = require('./combinations');
const left = '<';
const right = '>';
const plus = '+';
const minus = '-';


var resultLine = argv._.join(" ");

if (argv.f) {
  resultLine = fs.readFileSync(argv.f, 'utf8');
}

const euclidean = function(a, b) {
  return Math.sqrt(Math.pow(a - b, 2));
};

const euclideanSqr = function(a, b) {
  return Math.pow(a - b, 2);
};

var analysis = function(line) {
  var temp = [];
  for (let i in line) {
    temp.push(line.charCodeAt(i));
  }
  //find clasters
  var distances = [];
  for (let item of temp){
    if (item === -1)
      continue;
    let distance = [parseInt(item)];
    for (let i = 0; i < temp.length; i++) {
      let d = euclideanSqr(parseInt(item), parseInt(temp[i]));
      if (d < 100) {
        distance.push(parseInt(temp[i]));
        temp[i] = -1;
      }
    }
    distances.push(distance);
  }
  //Root mean square
  var rms = [];
  distances.forEach(function(item) {
    let res = Math.sqrt(item.reduce((prev, current) => {
      return prev + Math.pow(current, 2);
    }, 0) / item.length);
    rms.push(Math.round(res));
  }, this);

  return rms;
};

const findNearest = function(chars, number) {
  var pos = chars.lastIndexOf(number);
  if (pos !== -1) {
    return pos;
  }
  var nearest = 0;
  var distance = 255;
  for (var i = 0; i < chars.length; i++) {
    let temp = euclidean(chars[i], number);
    if (temp < distance) {
      distance = temp;
      nearest = i;
    }
  }
  return nearest;
};

const origCharTable = analysis(resultLine);
console.log(origCharTable, origCharTable.length);
const variousCharTables = combinations(origCharTable);
// variousCharTables = [origCharTable];
console.log("step2");

var finalProgram;
variousCharTables.forEach((charTable) => {
  // console.log(`Current charTable is ${charTable}`);
  var line = '';
  var charPos = [];
  var memPos = 0;
  for (let char of charTable) {
    line += numbers[char];
    charPos.push(parseInt(char));
    line += ">";
    ++memPos;
  }

  for (var i = 0; i < resultLine.length; i++) {
    let currentNumber = resultLine.charCodeAt(i);
    var pos = findNearest(charPos, currentNumber);
    var shift = memPos - pos;
    if (shift > 0) {
      line += left.repeat(shift);
    } else {
      line += right.repeat(-shift);
    }
    memPos = pos;
    if (currentNumber !== charPos[pos]) {
      if (currentNumber > charPos[pos]) {
        line += plus.repeat(currentNumber - charPos[pos]);
      } else {
        line += minus.repeat(charPos[pos] - currentNumber);
      }
      charPos[pos] = currentNumber;
    }
    line += '.';
  }

  // Hack remoce <>
  line = line.replace(/<>/g, '');
  // console.log(`Current program legth is ${line.length}`);
  if (!finalProgram || finalProgram.length > line.length)
    finalProgram = line;
});

var outFilename = argv.o || 'out.b';

console.log(finalProgram);
console.log(`Final size is ${finalProgram.length} byte, out filename ${outFilename}`);
fs.writeFile(outFilename, finalProgram, (err) => {if (err) console.error(err);});
