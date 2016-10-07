#!/usr/bin/env node

const fs = require('fs');
const argv = require('minimist')(process.argv.slice(2));
const prompt = require('prompt-sync')();

const mem = new Array(3000000);
mem.fill(0);

var position = 0;
var exec = 0;
const rangeStack = [];
const prog = fs.readFileSync(argv._[0]).toString();

const prettyPrint = function() {
    console.log("Exec pos ", exec);
    if (position > 6) {
        console.log("Mem is", mem[position], " ", mem.slice(position - 5, position + 5));
    } else {
        console.log("Mem is", mem[position], " ", mem.slice(0, 10));
    }
    if (exec > 6) {
        console.log("Prog ", exec, prog[exec], "text:", prog.slice(exec - 5, exec + 5));
    } else {
        console.log("Prog ", exec, prog[exec], "text:", prog.slice(0, 10));
    }
    console.log("");
};


while (exec < prog.length) {

    /*if(mem[position] < 0){
        process.exit();
    }*/
    //prettyPrint();
    switch (prog[exec]) {
        case '+':
            mem[position]++;
            break;
        case '-':
            mem[position]--;
            break;
        case '>':
            position++;
            break;
        case '<':
            position--;
            break;
        case '.':
            process.stdout.write(String.fromCharCode(mem[position]));
            //console.log(String.fromCharCode(mem[position]));
            break;
        case ',':
            var p = prompt("");
            if (p.length === 0) {
                mem[position] = 10;
            } else {
                mem[position] = p.charCodeAt(0);
            }
            //console.log(mem[position]);
            break;
        case '[':
            if (mem[position] === 0) {
                var inner = 0;
                var found = true;
                //console.log('Start', exec, prog[exec]);
                exec++;
                while (found) {
                    //console.log('Step', prog[exec]);

                    if (prog[exec] === '[') {
                        //console.log('Inner start!', exec, prog[exec]);
                        inner++;
                    }
                    if (inner === 0 && prog[exec] === ']') {
                        //console.log('End!', exec, prog[exec]);
                        found = false;
                    } else if (inner > 0 && prog[exec] === ']') {
                        //console.log('Inner end!', exec, prog[exec]);
                        inner--;
                    }

                    if (exec > prog.length) {
                        console.error('Don\'t close ]');
                        process.exit();
                    }
                    exec++;

                }
                exec--;
                //console.log('Pos in end!', exec, prog[exec]);
            } else {
                //console.log('Push to rangeStack', rangeStack);
                rangeStack.push(exec);
            }
            break;
        case ']':
            //console.log(rangeStack);
            if (mem[position] === 0) {
                rangeStack.pop();
            } else {
                if (rangeStack.length < 1){
                    console.error('rangeStack.length < 1');
                    process.exit();
                }
                exec = rangeStack[rangeStack.length - 1];
                //console.log(exec);
            }
            break;
        default:
            break;
    }
    if (exec === undefined || position === undefined) {
        console.error('Status carrupted', exec, position, rangeStack);
        process.exit();
    }
    //prompt("Step");
    exec++;
}
