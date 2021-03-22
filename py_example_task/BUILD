"""
Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.

NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

load("//engine/build:isaac.bzl", "isaac_pkg","isaac_cc_library", "isaac_cc_module", "isaac_component")

# Create a filegroup to be able to include this file in documentation
filegroup(
    name = "doc",
    srcs = ["py_example_task.py"],
    visibility = ["//visibility:public"],
)



py_binary(
    name = "py_example_task",
    srcs = [
        "__init__.py",
        "py_example_task.py",
    ],
    data = [
        "//apps/py_example_task:py_example_task.app.json",
        "//packages/navsim/apps:navsim_navigation_subgraph",
        "//packages/navigation/apps:differential_base_navigation_subgraph",
        "//messages",
        "//packages/ml:libml_module.so",
        "//packages/ml:libtensorflow_module.so",
        "//messages:collision_proto",
        "//packages/navigation:libnavigation_module.so",
        "//packages/perception:libperception_module.so",
        "//packages/viewers:libviewers_module.so",
        "//packages/utils:libutils_module.so",
    ],
    deps = ["//engine/pyalice"],
)

isaac_pkg(
    name = "py_example_task-pkg",
    srcs = ["py_example_task"],
)
