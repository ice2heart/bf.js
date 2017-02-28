#!/usr/bin/env node

const fs = require('fs');
const argv = require('minimist')(process.argv.slice(2));
const prompt = require('prompt-sync')();

class BfExec {
  constructor(program, maxCycleCount) {
    this.mem = new Buffer(3000000);
    this.mem.fill(0);

    this.position = 0;
    this.exec = 0;
    this.rangeStack = [];
    this.maxCount = maxCycleCount;
    this.cycleCount = 0;
    this.prog = program;
  }

  prettyPrint() {
    console.log("Exec pos ", this.exec);
    if (this.position > 6) {
      console.log("Mem is", this.mem[this.position], " ", this.mem.slice(this.position - 5, this.position + 5));
    } else {
      console.log("Mem is", this.mem[this.position], " ", this.mem.slice(0, 10));
    }
    if (this.exec > 6) {
      console.log("Prog ", this.exec, this.prog[this.exec], "text:", this.prog.slice(this.exec - 5, this.exec + 5));
    } else {
      console.log("Prog ", this.exec, this.prog[this.exec], "text:", this.prog.slice(0, 10));
    }
  }

  doCycle() {
    if (this.maxCount && this.maxCount < this.cycleCount)
      return 1;
    switch (this.prog[this.exec]) {
    case '+':
      this.mem[this.position]++;
      break;
    case '-':
      this.mem[this.position]--;
      break;
    case '>':
      this.position++;
      break;
    case '<':
      this.position--;
      break;
    case '.':
      process.stdout.write(String.fromCharCode(this.mem[this.position]));
      break;
    case '$':
      process.stdout.write(String(this.mem[this.position]));
      break;
    case ',':
      var p = prompt("");
      if (p.length === 0) {
        this.mem[this.position] = 10;
      } else {
        this.mem[this.position] = p.charCodeAt(0);
      }
      break;
    case '@':
      this.prettyPrint();
      prompt("");
      break;
    case '[':
      if (this.mem[this.position] === 0) {
        var inner = 0;
        var found = true;
        this.exec++;
        while (found) {
          if (this.prog[this.exec] === '[') {
            inner++;
          }
          if (inner === 0 && this.prog[this.exec] === ']') {
            found = false;
          } else if (inner > 0 && this.prog[this.exec] === ']') {
            inner--;
          }

          if (this.exec > this.prog.length) {
            console.error('Don\'t close ]');
            throw ('runtime error');
          }
          this.exec++;
        }
        this.exec--;
      } else {
        this.rangeStack.push(this.exec);
      }
      break;
    case ']':
      if (this.mem[this.position] === 0) {
        this.rangeStack.pop();
      } else {
        if (this.rangeStack.length < 1) {
          console.error('rangeStack.length < 1');
          throw ('runtime error');
        }
        this.exec = this.rangeStack[this.rangeStack.length - 1];
      }
      break;
    default:
      break;
    }
    if (this.exec === undefined || this.position === undefined) {
      console.error('Status carrupted', exec, position, rangeStack);
      throw ('Status carrupted');
    }
    this.exec++;
    this.cycleCount++;
    return 0;
  }

  execute() {
    while (this.exec < this.prog.length) {
      if (this.doCycle())
        break;
    }
  }
}


const execute = argv.e;
var prog = '';
if (execute) {
  prog = execute;
} else if (argv._[0]) {
  prog = fs.readFileSync(argv._[0]).toString();
} else {
  console.error('No data');
}

const bf = new BfExec(prog, argv.cycle);
bf.execute();
