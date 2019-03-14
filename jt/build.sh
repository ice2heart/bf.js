#!/bin/sh
javac Main.java
jar cfm $1 Manifest.txt Main.class 
