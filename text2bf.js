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
}

const euclideanSqr = function(a, b) {
  return Math.pow(a - b, 2);
}

var analysis = function(line) {
  var temp = [];
  for (var i in line) {
    temp.push(line.charCodeAt(i));
  }
  //find clasters
  var distances = [];
  let item;
  while (item = temp.shift()) {
    if (item === -1)
      continue;
    let distance = [parseInt(item)];
    for (var i = 0; i < temp.length; i++) {
      let d = euclideanSqr(parseInt(item), parseInt(temp[i]));
      if (d < 30) {
        distance.push(parseInt(temp[i]));
        temp[i] = -1;
      };
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
}

const origCharTable = analysis(resultLine);
const variousCharTable = combinations(origCharTable);
console.log(variousCharTable);
var finalLine;
variousCharTable.forEach((charTable) => {
  var line = "";
  var charPos = []
  var memPos = 0;
  for (char of charTable) {
    line += numbers[char];
    charPos.push(parseInt(char));
    line += ">";
    ++memPos;
  }

  const findNearest = function(number) {
    var pos = charPos.lastIndexOf(number);
    if (pos !== -1) {
      return pos;
    }
    var nearest = 0;
    var distance = 255;
    for (var i = 0; i < charPos.length; i++) {
      let temp = euclidean(charPos[i], number);
      if (temp < distance) {
        distance = temp;
        nearest = i;
      }
    }
    return nearest;
  }

  for (var i = 0; i < resultLine.length; i++) {
    let currentNumber = resultLine.charCodeAt(i);
    var pos = findNearest(currentNumber);
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
  line = line.replace(/<>/g, "");
  console.log(line.length);
  if (!finalLine || finalLine.length > line.length)
    finalLine = line;
});

var outFilename = 'out.b';
if (argv.o) {
  outFilename = argv.o
}

console.log(`size is ${finalLine.length}`);
fs.writeFile(outFilename, finalLine);
