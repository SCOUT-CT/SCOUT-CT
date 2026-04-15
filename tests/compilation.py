import os
import glob
import subprocess
from .config import ConfigManager


def compile(args):
    
    configManager = ConfigManager().load_configs(args.config)
    bin_dir = configManager.test_config.cases_bin_dir
    comp_info_file = configManager.test_config.compiler_info_file
    comp = configManager.test_config.compiler

    makefiles = glob.glob(f"{configManager.test_config.cases_src_dir}/*/Makefile")

    base_dir = os.getcwd()

    gcc_info_result = subprocess.run([comp, "--version"], stdout=subprocess.PIPE)
    gcc_info_lines = gcc_info_result.stdout.decode('utf-8').split('\n')

    with open(os.path.join(bin_dir, comp_info_file), 'w') as f:
        f.write(gcc_info_lines[0])

    error_cnt = 0
    for mf in makefiles:
        dirname = os.path.dirname(mf)
        os.chdir(dirname)
        ret = os.system('make build-lib')
        if ret:
            error_cnt += 1
        os.chdir(base_dir)

    print(f"Nb compiling errors : {error_cnt}")

    error_cnt = 0
    for mf in makefiles:
        dirname = os.path.dirname(mf)
        os.chdir(dirname)
        ret = os.system('make')
        if ret:
            error_cnt += 1
        os.chdir(base_dir)
        
    print(f"Nb compiling errors : {error_cnt}")
