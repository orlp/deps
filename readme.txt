deps
======
_deps_ is a minimalistic building system for any process which consists of smaller processes that depend on eachother. You define processes and their dependencies, ask for an endresult, and deps will figure out which processes should be executed, and in what order. It works very similar to GNU make, but operates in an Python environment rather than the shell, and should run on any platform capable of running Python without any other dependencies.

deps is not a "framework" or a "software package". It is a library to write your own build scripts. This means that you have full control, even over the interface.

Can deps only be used for Python?
-----------------------------------
__No!__ In fact, I suspect that it will be _less_ used for Python projects than others, as Python projects typically do not have a build step. deps is targeted to be used for projects that have processes that have many dependent substeps, such as compiled languages like C/C++. But deps is by design language-agnostic, so you can use it for compressing and emailing log files, your LaTeX builds, etc.

Does deps use makefiles?
--------------------------
__No.__ Makefiles are a common anti-pattern seen with other build tools that deps tries to avoid. They insult the programmers capability of problem solving by replacing a programming language with a very inflexible fixed format. They might seem a good idea because they are so _readable and terse_, but this advantage quickly disappears as the makefile grows in size and complexity.

Instead, deps is a self-contained single-file Python module. Your actual build script can be contained in one, or if you so prefer, multiple files.

Will deps automatically find compilers, libraries and headers?
----------------------------------------------------------------
__Not really.__ To keep things simple and abstract deps is deliberately designed to __not__ be an "autoconf" tool. Build environments are very complicated and differ wildy from project to project and platform to platform. Trying to use tools that claim to set up a "write once, build everywhere" environment often requires more time and effort than to write a simple script to resolve the non-portable aspects, if you succeed at all.

However, I am a strong believer in "sane defaults". deps ships with some default process templates for common tasks like executing a shell command, compiling a C or C++ file and linking object files. These templates are very simple - they are designed to get you through a simple project, but it's expected that a more complicated project will take these as a base and extend them with more options. This is core throughout deps's design: everything works out of the box, but you can hook and extend it all.

How does deps work then?
--------------------------
deps is designed as a single-file library with a simple, but flexible API. This means it's easy to ship with your project so your users do not need to install more software than just a Python interpreter to build. A project using deps typically only has two files: deps.py and your build script, let's say build.py. As an example, here's a complete build script for a simple hello world C project:

    import deps
    
    deps.process("*.o", deps.c_compiler, "{p}.c")
    deps.process("hello" + deps.exe_ext, deps.c_linker, "hello.o")
    deps.process(":clean", deps.auto_clean)
    
    deps.build()

To build your project you'd simply type `python build.py`. By default deps will build all files that are not an input for something else - all endresults. globs are not considered for this - endresults have to be concrete. To clean up the code repository you'd write `python build.py :clean`.



Each process you define will require any amount of inputs (also called dependencies) and produce one output. By default inputs and outputs are assumed to be files, but they can be virtual as well, for example a process that only sets up environment variables will have a virtual output. Virtual inputs/outputs are prefixed with a `:`. To match an output you can also use Unix-style globs as well as a boolean matching function that returns True if it matches the requested output. For each string input `.format` will be called with `o`, `p`, `d`, `f`, `e` respectively defined as the original output, the full path of the output minus extension, its containing directory (without trailing slash), the filename and its extension without a dot. For virtual inputs only `v` is defined, set to the output name without colon. It is also possible to pass a function as input, it will be called with a dictionary filled with the above parameters and its results are used as inputs.

It is possible to end up defining two processes that could potentially generate one output. When using globs such as `*.c` this is almost guaranteed to happen. deps will always attempt to match each process entry from last-entered to first. This means that order matters, and you should put more "general" processes first, and specialize later.

Note that in the above example we used `deps.c_compiler`, `deps.c_linker`, `deps.exe_ext`, `deps.auto_clean`. These are predefined tools to make life a bit easier. `c_compiler` and `c_linker` are process templates that use simple default commands to invoke a C compiler and linker. `exe_ext` is defined as ".exe" on Windows, and the empty string on other platforms. `auto_clean` is a helpful little process that will clean up any file outputs, resulting in a clean source repository. A full description of all these helpers are down below.

deps works in two phases. In the first phase it will scan for dependencies, starting at the endresult(s). For each dependency it encounters it checks if there are any processes that produce it. If there are it will select the correct one (see above) and recursively check for its dependencies. If there are no processes that produce a file dependency, but it exists, then the dependency is considered to be met. If any dependency is missing deps errors. An error is also produced if a cyclic dependency is detected.

The second phase will determine which processes actually need to be run and run them. A process will run if any of the following are true:

1. It has no inputs.
2. It has a virtual output that is needed.
3. The process has a virtual input and the process that produced the virtual input has run.
4. All processes that produce the dependencies of the process have conclusively run or not run. An output file of this process has a last-written timestamp older than an input file.

However, after this has been decided the result can be passed into an optional callback that has the last say in whether or not the process should run. Then, the process is run. deps will attempt to run processes in parallel, if possible.