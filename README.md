# Bf.js [![Code Climate](https://lima.codeclimate.com/github/ice2heart/bf.js/badges/gpa.svg)](https://lima.codeclimate.com/github/ice2heart/bf.js) [![Issue Count](https://lima.codeclimate.com/github/ice2heart/bf.js/badges/issue_count.svg)](https://lima.codeclimate.com/github/ice2heart/bf.js)
## Yet another brainfuck interpreter and text2bf

Simple bf interpreter and text to bf code app. It's require node.js >= 6.9.0

## How to install

```
git clone git@github.com:ice2heart/bf.js.git; cd bf.js; npm i
```

## How to use interpreter

Simple use:

```
./bf.js test/Beer.b
```

Options:

-e Evaluate script
```
./bf.js -e='-[----->+<]>--.+.+.'
```

--cycle limit execute cycles:
```
./bf.js --cycle=30000 test/Beer.b
```

## How to use text2bf

```
./text2bf.js 'Hello world'
```

Default output file is 'out.b'

-o output filename

```
./text2bf.js 'Hello world' -o test.b
```

-f input filename

```
./text2bf.js -f text.ascii
```
