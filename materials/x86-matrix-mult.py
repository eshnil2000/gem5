# Copyright (c) 2024 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
"""

import argparse

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)
from gem5.components.processors.simple_switchable_processor import (
    SimpleSwitchableProcessor,
)


from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_l3_cache_hierarchy import (
    PrivateL1SharedL2L3CacheHierarchy
)


parser = argparse.ArgumentParser(
    description="This script shows how to use a suite. In this example, we "
    "will use the ARM Getting Started Benchmark Suite, and show "
    "the different functionalities of the suite.",
)

# Obtain the ARM "Getting Started" Benchmark Suite.
#microbenchmarks = obtain_resource("arm-getting-started-benchmark-suite")
microbenchmarks = obtain_resource("x86-matrix-multiply-run")
#test
# Give these as an option to the user to select and run the benchmark of their
# choice.
""" parser.add_argument(
    "benchmark",
    type=str,
    choices=[benchmark.get_id() for benchmark in microbenchmarks],
    help=f"The benchmark from the {microbenchmarks.get_id()} suite to run.",
)

# Get the arguments from the command line parser.
args = parser.parse_args()

# get the benchmark from the suite the user selected.
benchmark = None
for option in microbenchmarks:
    if option.get_id() == args.benchmark:
        benchmark = option
        break
 """

# This check ensures the gem5 binary is compiled to the ARM ISA target. If not,
# an exception will be thrown.
#requires(isa_required=ISA.ARM)
requires(isa_required=ISA.X86)

# In this setup we don't have a cache. `NoCache` can be used for such setups.
#cache_hierarchy = NoCache()
# Here we setup a MESI Two Level Cache Hierarchy.
cache_hierarchy = MESITwoLevelCacheHierarchy(
    l1d_size="1kB",
    l1d_assoc=8,
    l1i_size="1kB",
    l1i_assoc=8,
    l2_size="1MB",
    l2_assoc=16,
    num_l2_banks=2,
)

cache_hierarchy = PrivateL1SharedL2L3CacheHierarchy(
    l1d_size="1kB",
    l1d_assoc=8,
    l1i_size="1kB",
    l1i_assoc=8,
    l2_size="32kB",
    l2_assoc=16,
    l3_size="1MB",
    l3_assoc=16,
    l3_tag_latency=10,
    l3_data_latency=10,#write latency
    l3_response_latency=100 #read latency
)

# We use a single channel DDR3_1600 memory system
#memory = SingleChannelDDR3_1600(size="32MB")
memory = SingleChannelDDR3_1600(size="1MB")

# We use a simple Timing processor with one core.
#processor = SimpleProcessor(cpu_type=CPUTypes.TIMING, isa=ISA.ARM, num_cores=1)
#processor = SimpleProcessor(cpu_type=CPUTypes.O3, isa=ISA.X86, num_cores=1)
processor = SimpleSwitchableProcessor(
    starting_core_type=CPUTypes.TIMING,
    switch_core_type=CPUTypes.O3,
    isa=ISA.X86,
    num_cores=2,
)

# The gem5 library simble board which can be used to run simple SE-mode
# simulations.
board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Here we set the benchmark to run on the board. This is dependent on what the
# user has selected.
#board.set_workload(workload=benchmark)
board.set_workload(workload=microbenchmarks)
# Lastly we run the simulation.
simulator = Simulator(board=board)
simulator.run()
