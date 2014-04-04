import collections
import fnmatch
import os

class Deps(object):
    Process = collections.namedtuple("Process", ["output", "func", "deps", "should_run"])

    def __init__(self):
        self.processes = []

    def process(self, output, func, *deps, **kwargs):
        self.processes.insert(0, self.Process(output, func, deps, kwargs.get("should_run", lambda yn: yn)))

    def build(self, *endresults, **kwargs):
        parallel = kwargs.get("parallel", 4)
        max_depth = kwargs.get("max_depth", 100)

        # first get all the processes that need to run to satisfy all dependencies
        # we also detect any missing/cyclic dependencies at this stage
        processes, consumers = self._resolve_deps(list(endresults), max_depth)
        ready_to_run = [process for process in processes if not process.deps]
        outputs_handled = set()
        outputs_run = set()

        while ready_to_run:
            process = ready_to_run.pop()

            if self._should_run(process, outputs_run):
                result = process.func(process.output, process.deps)
                outputs_run.add(process.output)
                print("run: " + process.output)
            else:
                print("dont run: " + process.output)
            outputs_handled.add(process.output)

            for consumer in consumers[process.output]:
                for dep in consumer.deps:
                    if dep not in outputs_handled: break
                else:
                    ready_to_run.append(consumer)

            del consumers[process.output]

    def _resolve_deps(self, unresolved_deps, max_depth):
        processes, consumers = [], collections.defaultdict(list)
        resolved_deps = set()

        while unresolved_deps:
            unresolved_dep = unresolved_deps.pop()
            if unresolved_dep in resolved_deps: continue

            process = self._get_process_for_dep(unresolved_dep)
            processes.append(process)
            resolved_deps.add(unresolved_dep)

            for dep in process.deps:
                if dep in unresolved_deps or dep == process.output:
                    raise Exception("cyclic dependency while attempting to resolve resource \"{}\"".format(dep))

                consumers[dep].append(process)
                unresolved_deps.append(dep)

            print(len(unresolved_deps))

            if len(unresolved_deps) > max_depth:
                raise Exception("max depth exceeded while attempting to resolve resource \"{}\"".format(dep))

        return processes, consumers

    def _get_process_for_dep(self, dep):
        for process in self.processes:
            if (
                hasattr(process.output, "__call__") and process.output(dep) or
                dep == process.output or
                not dep.startswith(":") and fnmatch.fnmatch(dep, process.output)
            ):
                return self.Process(dep, process.func, self._format_deps(dep, process.deps), process.should_run)

        if not dep.startswith(":") and os.path.exists(dep):
            return self.Process(dep, lambda out, deps: None, [], lambda yn: yn)
 
        raise Exception("no process found producing \"{}\"".format(dep))

    def _format_deps(self, output, deps):
        if output.startswith(":"):
            params = {"v": output[1:]}
        else:
            params = {
                "o": output,
                "p": os.path.splitext(output)[0],
                "d": os.path.dirname(output),
                "f": os.path.splitext(os.path.basename(output))[0],
                "e": os.path.splitext(output)[1][1:],
            }

        return [dep.format(**params) for dep in deps]

    def _should_run(self, process, outputs_run):
        run = False

        if not process.deps:
            run = True
        elif process.output.startswith(":"):
            run = True
        elif any(dep.startswith(":") and dep in outputs_run for dep in process.deps):
            run = True
        else:
            try:
                last_modification = os.path.getmtime(process.output)
            except os.error:
                run = True
            else:
                for dep in process.deps:
                    if dep.startswith(":"): continue

                    try:
                        last_modification_dep = os.path.getmtime(dep)
                    except os.error:
                        run = True
                        break
                    else:
                        if last_modification <= last_modification_dep:
                            run = True
                            break

        return process.should_run(run)


_main_deps = Deps()

def process(*args, **kwargs):
    _main_deps.process(*args, **kwargs)

def build(*args, **kwargs):
    _main_deps.build(*args, **kwargs)




import subprocess
import platform

if platform.system() == "Windows":
    executable_ext = ".exe"
else:
    executable_ext = ""

def auto_clean(target_name, deps):
    pass

def c_compiler(target_name, deps):
    print("compiling {}, {}".format(target_name, " ".join(deps)))
    subprocess.call(["gcc", "-o", target_name, "-c"] + deps)

def c_linker(target_name, deps):
    print("linking {}, {}".format(target_name, " ".join(deps)))
    subprocess.call(["gcc", "-o", target_name + executable_ext] + deps)