"""
Unit tests for plassembler.

Usage: pytest

"""

# import
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

import pytest
from loguru import logger

# import functions

# data
test_data = Path("tests/test_data")
end_to_end = Path(f"{test_data}/end_to_end")
plassembler_db_dir = Path(f"{test_data}/Plassembler_Test_DB")


# make fake tempdir for testing
@pytest.fixture(scope="session")
def tmp_dir(tmpdir_factory):
    return tmpdir_factory.mktemp("tmp")


# to ensure sys exit on logger error
logger.add(lambda _: sys.exit(1), level="ERROR")
# import functions


def remove_directory(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


def exec_command(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    """executes shell command and returns stdout if completes exit code 0
    Parameters
    ----------
    cmnd : str
      shell command to be executed
    stdout, stderr : streams
      Default value (PIPE) intercepts process output, setting to None
      blocks this."""

    proc = subprocess.Popen(cmnd, shell=True, stdout=stdout, stderr=stderr)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FAILED: {cmnd}\n{err}")
    return out.decode("utf8") if out is not None else None


def test_plassembler_download():
    """test plassembler download"""
    fake_db = f"{end_to_end}/db"
    cmd = f"plassembler download -d {fake_db}"
    exec_command(cmd)
    remove_directory(fake_db)


def test_citation():
    """test plassembler citation"""
    cmd = "plassembler citation"
    exec_command(cmd)


# test running end to end
# for cases 1,2,3
# uncomment for mac running to check
# 70kbp, 44kbp and 9kbp plasmid reads are from
# the 70kbp is a fake chromosome


class test_end_to_end(unittest.TestCase):
    def test_plassembler_case_1(self):
        """test plassembler run - chromosome only assembled with Flye, no plasmids - plasmids recovered from the short reads"""
        longreads: Path = f"{end_to_end}/case1.fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_case_1_use_raven(self):
        """test plassembler run - chromosome only assembled with Flye, no plasmids - plasmids recovered from the short reads"""
        longreads: Path = f"{end_to_end}/case1.fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_case_2(self):
        with self.assertRaises(RuntimeError):
            """test plassembler run case 2 no chromosome assembled at all"""
            longreads: Path = f"{end_to_end}/input_fastq.gz"
            s1: Path = f"{end_to_end}/input_R1.fastq.gz"
            s2: Path = f"{end_to_end}/input_R2.fastq.gz"
            chromosome = 500000  # higher than 70k
            outdir: Path = f"{end_to_end}/test_out"
            cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f"
            exec_command(cmd)
            remove_directory(outdir)

    def test_plassembler_case_3(self):
        """test plassembler run - chromosome and plasmids assembled with Flye"""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_case_4(self):
        """test plassembler run case 4. Only chromosome assembled with flye, no plasmid in recovery."""
        longreads: Path = f"{end_to_end}/abaumanii_plasmid.fastq.gz"
        s1: Path = f"{end_to_end}/abaumanii_reads_R1.fastq.gz"
        s2: Path = f"{end_to_end}/abaumanii_reads_R2.fastq.gz"
        chromosome = 100000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_multiple_chromosomes_no_plasmids(self):
        """test plassembler run where multiple chromosomes are assembled but no plasmid (ATCC 17802 errored out in v 1.4.0)"""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        s1: Path = f"{end_to_end}/input_atcc17802_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_atcc17802_R2.fastq.gz"
        chromosome = 5000  # fake low chrom length
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f"
        exec_command(cmd)
        remove_directory(outdir)

    # copy number

    def test_plassembler_case_depth_filter_all(self):
        """test plassembler run depth_filter 1.2 - will have no plasmids left"""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f --depth_filter 1.2"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_case_depth_filter_some(self):
        """test plassembler run depth_filter 0.6 with input_half lr - will have only 1 plasmid"""
        longreads: Path = f"{end_to_end}/input_half.fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f --depth_filter 0.6"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_case_extra_unicycler_spades_opts(self):
        """test plassembler with extra unicycler and spades opts"""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        temp_dir: Path = f"{end_to_end}/temp"
        cmd = f'plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f   --unicycler_options "--no_rotate --mode conservative" --spades_options "--tmp-dir  {temp_dir}" '
        exec_command(cmd)
        remove_directory(outdir)

    # skipqc

    def test_plassembler_skipqc(self):
        """test plassembler run case 1. With --skip_qc. Only chromosome assembled with flye, no plasmid in recovery."""
        longreads: Path = f"{end_to_end}/case1.fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f --skip_qc"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_skipqc_no_gzip(self):
        """test plassembler run case 1. With --skip_qc but with raw FASTQ input (issue 60 - rrwick). Only chromosome assembled with flye, no plasmid in recovery."""
        longreads: Path = f"{end_to_end}/case1.fastq"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f --skip_qc"
        exec_command(cmd)
        remove_directory(outdir)

    # skip_mash

    def test_plassembler_skipmash(self):
        """test plassembler run case 1. With --skip_mash. No need for -d"""
        longreads: Path = f"{end_to_end}/case1.fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2}  -o {outdir}  -t 8 -f --skip_mash"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_flye_assembly_info(self):
        """test plassembler run case 4. With flye assembly and flye info."""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        flye_dir: Path = f"{end_to_end}/test_flye_dir"
        chromosome = 50000
        flye_assembly: Path = f"{flye_dir}/assembly.fasta"
        flye_info: Path = f"{flye_dir}/assembly_info.txt"
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 --flye_assembly {flye_assembly} --flye_info {flye_info} -f"
        exec_command(cmd)
        remove_directory(outdir)

    # flye_dir
    def test_plassembler_flye_dir(self):
        """test plassembler run case 4. With flye directory."""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        flye_dir: Path = f"{end_to_end}/test_flye_dir"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 --flye_directory {flye_dir} -f"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_flye_info_missing(self):
        """test missing --flye_assembly. Assembly conducted anyway."""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        flye_dir: Path = f"{end_to_end}/test_flye_dir"
        chromosome = 50000
        flye_assembly: Path = f"{flye_dir}/assembly.fasta"
        flye_info: Path = f"{flye_dir}/assembly_info.txt"
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 --flye_assembly {flye_assembly} -f"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_flye_assembly_missing(self):
        """test missing --flye_assembly. Assembly conducted anyway."""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        flye_dir: Path = f"{end_to_end}/test_flye_dir"
        chromosome = 50000
        flye_assembly: Path = f"{flye_dir}/assembly.fasta"
        flye_info: Path = f"{flye_dir}/assembly_info.txt"
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 --flye_info {flye_info} -f"
        exec_command(cmd)
        remove_directory(outdir)

    """
    long
    """

    def test_plassembler_long(self):
        """test plassembler long"""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler long -l {longreads} -c {chromosome} -d {plassembler_db_dir} -o {outdir}  -t 8 -f"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_long_skipmash(self):
        """test plassembler long --skip_mash - no need for -d"""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler long -l {longreads} -c {chromosome} -o {outdir}  -t 8 -f --skip_mash"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_depth_all(self):
        """test plassembler long depth filter will all plasmids filtered"""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler long -l {longreads} -c {chromosome} -d {plassembler_db_dir} -o {outdir} --depth_filter 10 -t 8 -f"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_depth_some(self):
        """test plassembler long depth filter will some plasmids filtered"""
        longreads: Path = f"{end_to_end}/input_depth_filter.fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler long -l {longreads} -c {chromosome} -d {plassembler_db_dir} -o {outdir} --depth_filter 2  -t 8 -f"
        exec_command(cmd)
        remove_directory(outdir)

    # def test_plassembler_long_canu(self):
    #     """test plassembler long canu"""
    #     longreads: Path = f"{end_to_end}/input_fastq.gz"
    #     chromosome = 50000
    #     outdir: Path = f"{end_to_end}/test_out"
    #     cmd = f"plassembler long -l {longreads} -c {chromosome} -d {plassembler_db_dir} -o {outdir}  -t 8 -f  --canu_flag"
    #     exec_command(cmd)
    #     remove_directory(outdir)

    def test_plassembler_long_no_chrom(self):
        with self.assertRaises(RuntimeError):
            """test plassembler long - no chromosome recovered - should error out"""
            longreads: Path = f"{end_to_end}/input_fastq.gz"
            chromosome = 500000
            outdir: Path = f"{end_to_end}/test_out"
            cmd = f"plassembler long -l {longreads} -c {chromosome} -d {plassembler_db_dir} -o {outdir}  -t 8 -f"
            exec_command(cmd)
            remove_directory(outdir)

    def test_plassembler_long_no_plasmids(self):
        """test plassembler long - no plasmids recovered at all"""
        longreads: Path = f"{end_to_end}/abaumanii_plasmid.fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler long -l {longreads} -c {chromosome} -d {plassembler_db_dir} -o {outdir}  -t 8 -f"
        exec_command(cmd)
        remove_directory(outdir)

    """
    
    --no_chromosome

    """

    def test_plassembler_run_no_chromosome(self):
        """test plassembler run with --no_chromosome"""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        chromosome = 500000  # higher than 70k
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler run -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir}  -t 8 -f --no_chromosome"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_long_no_chromosome(self):
        """test plassembler long with --no_chromosome"""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        chromosome = 50000
        outdir: Path = f"{end_to_end}/test_out"
        cmd = f"plassembler long -l {longreads} -c {chromosome} -d {plassembler_db_dir} -o {outdir}  -t 8 -f --no_chromosome"
        exec_command(cmd)
        remove_directory(outdir)

    """
    assembled
    """

    def test_plassembler_assembled(self):
        """test plassembler assembled"""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        outdir: Path = f"{end_to_end}/test_out"
        chromosome = 50000
        input_plasmids = f"{end_to_end}/test_plasmids.fasta"
        input_chromosome = f"{end_to_end}/test_chromosome.fasta"
        cmd = f"plassembler assembled -l {longreads} -c {chromosome} -1 {s1} -2 {s2} -d {plassembler_db_dir} -o {outdir} --input_plasmids {input_plasmids} --input_chromosome {input_chromosome}  -t 8 -f"
        exec_command(cmd)
        remove_directory(outdir)

    def test_plassembler_assembled_no_copy_numbers(self):
        """test plassembler assembled --no_copy_numbers"""
        longreads: Path = f"{end_to_end}/input_fastq.gz"
        s1: Path = f"{end_to_end}/input_R1.fastq.gz"
        s2: Path = f"{end_to_end}/input_R2.fastq.gz"
        outdir: Path = f"{end_to_end}/test_out"
        chromosome = 50000
        input_plasmids = f"{end_to_end}/test_plasmids.fasta"
        input_chromosome = f"{end_to_end}/test_chromosome.fasta"
        cmd = f"plassembler assembled -c {chromosome} --no_copy_numbers -d {plassembler_db_dir} -o {outdir} --input_plasmids {input_plasmids} -t 8 -f"
        exec_command(cmd)
        remove_directory(outdir)
