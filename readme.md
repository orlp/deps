###Warning: development is in an alpha stage.
###The documentation and code ~~may~~ will contain bugs and the API might change when you blink.

deps
======
_deps_ is a minimalistic building system for any process which consists of smaller processes that depend on each other. You define processes and their dependencies, ask for an endresult, and deps will figure out which processes should be executed, and in what order. It works very similar to GNU make, but operates in an Python environment rather than the shell, and should run on any platform capable of running Python without any other dependencies.

deps is not a "framework" or a "software package". It is a library to write your own build scripts. This means that you have full control, even over the interface.

###Can deps only be used for Python?
__No!__ In fact, I suspect that it will be _less_ used for Python projects than others, as Python projects typically do not have a build step. deps is targeted to be used for projects that have processes that have many dependent substeps, such as compiled languages like C/C++. But deps is by design language-agnostic, so you can use it for compressing and emailing log files, your LaTeX builds, etc.

###Does deps use makefiles?
__No.__ Makefiles are a common anti-pattern seen with other build tools that deps tries to avoid. They insult the programmers capability of problem solving by replacing a comfortable programming language with an obscure inflexible format. They might seem a good idea because they are so _readable and terse_, but this advantage quickly disappears as the makefile grows in size and complexity.

Instead, deps is a self-contained single-file Python module. Your actual build script can be contained in one, or if you so prefer, multiple files. There is no changed syntax or weirdness, your build script is a regular Python script, executed like any other.

###Will deps automatically find compilers, libraries and headers?
__Not really.__ To keep things simple and abstract deps is deliberately designed to __not__ be an "autoconf" tool. Build environments are very complicated and differ wildy from project to project and platform to platform. Trying to use tools that claim to set up a "write once, build everywhere" environment often requires more time and effort than to write a simple script to resolve the non-portable aspects, if you succeed at all.

However, I am a strong believer in "sane defaults". deps ships with some default process templates for common tasks like executing a shell command, compiling a C or C++ file and linking object files. These templates are very simple - they are designed to get you through a simple project, but it's expected that a more complicated project will take these as a base and extend them with more options. This is core throughout deps's design: everything works out of the box, but you can hook and extend it all.

###What _can_ deps do?

So far most of this readme was aimed at _removing_ assumptions as to what deps is. Here's some things deps actually can do:
 - Set up processes that have an output, a function to call to produce that output, and any amount of dependencies.
 - Lazy top-down dependency resolution. We start at the endresult and keep adding producing processes until all dependencies have been resolved. A process isn't considered unless it can  produce a required dependency.
 - Circular dependency detection.
 - Set up complex dependency relations through callbacks. Instead of directly naming the output of a process it's possible to have a "template process" that matches a glob or even an  arbitrary filter function. The dependencies of the process can be a function of the required output.
 - Lazy execution. If an output does not need to be updated the process is not run. The exact rules are in the docs, but this is only default behaviour - it can be overriden.
 - Parallel execution. If possible deps will run processes in parallel up to a degree configurable by you.


###How does deps work then?
deps is designed as a single-file library with a simple, but flexible API. This means it's easy to ship with your project so your users do not need to install more software than just a Python interpreter to build. A project using deps typically only has two files: `deps.py` and your build script, let's say `build.py`. As an example, here's a complete build script for a simple hello world C project:

```python
import deps

deps.process("*.o", deps.c_compiler, "{p}.c")
deps.process("hello" + deps.exe_ext, deps.c_linker, "hello.o")
deps.process(":clean", deps.auto_clean)

deps.build()
```

To build your project you'd simply type `python build.py`. By default deps will build all explicit files that are not an input for something else - all endresults. To clean up the code repository leaving only source code you'd write `python build.py :clean`. To understand exactly what's going on, read the docs.
