import os
import subprocess
import collections
import platform

if platform.system() == "Windows":
    executable_ext = ".exe"
else:
    executable_ext = ""

def ccompiler(target_name, deps):
    print("compiling {}, {}".format(target_name, " ".join(deps)))
    subprocess.call(["gcc", "-o", target_name, "-c"] + deps)

def linker(target_name, deps):
    print("linking {}, {}".format(target_name, " ".join(deps)))
    subprocess.call(["gcc", "-o", target_name] + deps)

class Project(object):
    Target = collections.namedtuple("Target", ["name", "deps", "builder"])

    def __init__(self):
        self.targets = {}

    def target(self, target_name, builder, deps=None):
        if target_name in self.targets:
            print("warning - duplicate target name, overriding previous settings: \"{}\"".format(target_name))

        self.targets[target_name] = self.Target(target_name, self._flatten(deps), builder)

    def build(self, end_targets=None):
        if end_targets is None:
            all_depencies = set(sum((target.deps for target in self.targets.values()), []))
            end_targets = [target.name for target in self.targets.values() if target.name not in all_depencies]
        else:
            end_targets = flatten(end_targets)

        if not end_targets:
            raise Exception("no end targets found (cyclic dependency?)")

        for target in end_targets:
            try:
                last_modification = os.path.getmtime(target)
            except os.error:
                last_modification = 0

            self._build(end_targets, set(), last_modification)

    def _build(self, targets, illegal_cyclic_deps, rebuild_threshold):
        rebuild_needed = False

        for target in targets:
            if target not in self.targets:
                if os.path.exists(target):
                    last_modification = os.path.getmtime(target)
                    rebuild_needed |= last_modification >= rebuild_threshold
                else:
                    raise Exception("no rule found to build \"{}\"".format(target))
            else:
                target = self.targets[target]
                try:
                    last_modification = os.path.getmtime(target.name)
                except os.error:
                    last_modification = 0

                if not target.deps or self._build(target.deps, illegal_cyclic_deps | {target.name}, last_modification):
                    rebuild_needed = not target.builder(target.name, target.deps)

        return rebuild_needed or last_modification >= rebuild_threshold

    def _flatten(self, deps):
        if hasattr(deps, "__iter__"):
            return sum((self._flatten(dep) for dep in deps), [])
        
        return deps and [deps] or []