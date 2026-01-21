# Segfault

## Steps

```shell
~/.pyenv/versions/3.14.2t/bin/python -m venv venv
venv/bin/python -m pip install pip setuptools --upgrade
venv/bin/python -m pip install pytest Flask
venv/bin/python -m pip install --force-reinstall git+https://github.com/gorakhargosh/watchdog.git@refs/pull/1109/head
venv/bin/python -m pip install pytest-repeat pytest-xdist
```

```shell
# trigger segfault with 
venv/bin/python -m pytest -n auto --count 1000 tests/test_drafts.py
```

```
Fatal Python error: Segmentation fault

<Cannot show all threads while the GIL is disabled>
Stack (most recent call first):
  File "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/python3.14t/shutil.py", line 109 in _fastcopy_fcopyfile
  File "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/python3.14t/shutil.py", line 319 in copyfile
  File "/Users/cody.scott/code/segfault/tests/utils.py", line 33 in copy_file
  File "/Users/cody.scott/code/segfault/tests/utils.py", line 49 in copy_site_file
  File "/Users/cody.scott/code/segfault/tests/start.py", line 11 in start
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/click/core.py", line 824 in invoke
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/click/core.py", line 1269 in invoke
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/click/core.py", line 1406 in main
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/click/testing.py", line 504 in invoke
  File "/Users/cody.scott/code/segfault/tests/conftest.py", line 12 in run_start
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/fixtures.py", line 908 in call_fixture_func
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/fixtures.py", line 1202 in pytest_fixture_setup
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_callers.py", line 121 in _multicall
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_manager.py", line 120 in _hookexec
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_hooks.py", line 512 in __call__
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/fixtures.py", line 1110 in execute
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/fixtures.py", line 627 in _get_active_fixturedef
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/fixtures.py", line 539 in getfixturevalue
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/fixtures.py", line 707 in _fillfixtures
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/python.py", line 1723 in setup
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/runner.py", line 523 in setup
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/runner.py", line 165 in pytest_runtest_setup
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_callers.py", line 121 in _multicall
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_manager.py", line 120 in _hookexec
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_hooks.py", line 512 in __call__
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/runner.py", line 245 in <lambda>
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/runner.py", line 353 in from_call
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/runner.py", line 244 in call_and_report
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/runner.py", line 131 in runtestprotocol
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/runner.py", line 118 in pytest_runtest_protocol
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_callers.py", line 121 in _multicall
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_manager.py", line 120 in _hookexec
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_hooks.py", line 512 in __call__
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/xdist/remote.py", line 227 in run_one_test
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/xdist/remote.py", line 206 in pytest_runtestloop
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_callers.py", line 121 in _multicall
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_manager.py", line 120 in _hookexec
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_hooks.py", line 512 in __call__
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/main.py", line 372 in _main
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/main.py", line 318 in wrap_session
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/_pytest/main.py", line 365 in pytest_cmdline_main
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_callers.py", line 121 in _multicall
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_manager.py", line 120 in _hookexec
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/pluggy/_hooks.py", line 512 in __call__
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/xdist/remote.py", line 427 in <module>
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/execnet/gateway_base.py", line 1291 in executetask
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/execnet/gateway_base.py", line 341 in run
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/execnet/gateway_base.py", line 411 in _perform_spawn
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/execnet/gateway_base.py", line 389 in integrate_as_primary_thread
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/execnet/gateway_base.py", line 1273 in serve
  File "/Users/cody.scott/code/segfault/venv/lib/python3.14t/site-packages/execnet/gateway_base.py", line 1806 in serve
  File "<string>", line 8 in <module>
  File "<string>", line 1 in <module>

Current thread's C stack trace (most recent call first):
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _Py_DumpStack+0x44 [0x100f28a6c]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at faulthandler_fatal_error+0x240 [0x100f3c8dc]
  Binary file "/usr/lib/system/libsystem_platform.dylib", at _sigtramp+0x38 [0x1916fd6a4]
  Binary file "/usr/lib/system/libsystem_c.dylib", at filesec_free+0x18 [0x191561f18]
  Binary file "/usr/lib/system/libcopyfile.dylib", at copyfile_state_alloc+0x38 [0x19f8f6b38]
  Binary file "/usr/lib/system/libcopyfile.dylib", at copyfile_preamble+0x2c [0x19f8f69ec]
  Binary file "/usr/lib/system/libcopyfile.dylib", at fcopyfile+0x48 [0x19f8f8fd0]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at os__fcopyfile+0x90 [0x100f424e0]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_EvalFrameDefault+0x352c [0x100e854bc]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_Vector+0x2cc [0x100e81ce8]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at method_vectorcall+0x1bc [0x100d35424]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_EvalFrameDefault+0x3e40 [0x100e85dd0]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_Vector+0x2cc [0x100e81ce8]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at method_vectorcall+0xb4 [0x100d3531c]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyObject_Call+0x7c [0x100d320e8]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_EvalFrameDefault+0x3e40 [0x100e85dd0]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at gen_send_ex2+0x260 [0x100d5508c]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at gen_iternext+0x24 [0x100d536e8]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at builtin_next+0x64 [0x100e7e130]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_EvalFrameDefault+0x352c [0x100e854bc]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_Vector+0x2cc [0x100e81ce8]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyObject_VectorcallDictTstate+0x7c [0x100d31610]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyObject_Call_Prepend+0x98 [0x100d32894]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at call_method+0x7c [0x100de428c]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyObject_MakeTpCall+0x148 [0x100d3180c]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_EvalFrameDefault+0x4f7c [0x100e86f0c]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_Vector+0x2cc [0x100e81ce8]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyObject_VectorcallDictTstate+0x7c [0x100d31610]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyObject_Call_Prepend+0x98 [0x100d32894]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at call_method+0x7c [0x100de428c]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyObject_Call+0x118 [0x100d32184]
  Binary file "/Users/cody.scott/.pyenv/versions/3.14.2t/lib/libpython3.14t.dylib", at _PyEval_EvalFrameDefault+0x3e40 [0x100e85dd0]
  <truncated rest of calls>

Extension modules: markupsafe._speedups, yaml._yaml, _watchdog_fsevents (total: 3)
[gw11] node down: Not properly terminated
F
replacing crashed worker gw11
```