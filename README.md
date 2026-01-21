# Segfault

## Steps

```shell
~/.pyenv/versions/3.14.2t/bin/python -m venv venv
venv/bin/python -m pip install pip setuptools --upgrade
venv/bin/python -m pip install git+https://github.com/gorakhargosh/watchdog.git@refs/pull/1109/head
```

Trigger segfault with 

```shell
seq 1 14 | xargs -I{} -P 14 sh -c 'for i in $(seq 1 100); do venv/bin/python trigger.py || exit 1; done'
```

```
Fatal Python error: Segmentation fault

<Cannot show all threads while the GIL is disabled>
Stack (most recent call first):
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/watchdog/observers/fsevents.py", line 309 in run
  File "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/python3.14t/threading.py", line 1082 in _bootstrap_inner
  File "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/python3.14t/threading.py", line 1044 in _bootstrap

Current thread's C stack trace (most recent call first):
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _Py_DumpStack+0x44 [0x101144a6c]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at faulthandler_fatal_error+0x240 [0x1011588dc]
  Binary file "/usr/lib/system/libsystem_platform.dylib", at _sigtramp+0x38 [0x1916fd6a4]
  Binary file "/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/FSEvents.framework/Versions/A/FSEvents", at register_with_server+0xe8 [0x19aeee458]
  Binary file "/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/FSEvents.framework/Versions/A/FSEvents", at FSEventStreamStart+0xf4 [0x19aeee284]
  Binary file "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_watchdog_fsevents.cpython-314t-darwin.so", at watchdog_add_watch+0x380 [0x1008093fc]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at cfunction_call+0xb4 [0x100fbbaa4]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyObject_MakeTpCall+0x148 [0x100f4d80c]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_EvalFrameDefault+0x2364 [0x1010a02f4]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_Vector+0x2cc [0x10109dce8]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at method_vectorcall+0x13c [0x100f513a4]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at context_run+0x88 [0x1010d0a64]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_EvalFrameDefault+0x5c24 [0x1010a3bb4]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_Vector+0x2cc [0x10109dce8]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at method_vectorcall+0x13c [0x100f513a4]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at thread_run+0x80 [0x1011bf870]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at pythread_wrapper+0x1c [0x101141d0c]
  Binary file "/usr/lib/system/libsystem_pthread.dylib", at _pthread_start+0x88 [0x1916c3bc8]
  Binary file "/usr/lib/system/libsystem_pthread.dylib", at thread_start+0x8 [0x1916beb80]
```
