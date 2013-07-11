#!/usr/bin/python
import sys
import argparse
import os
from classes.Helpers import *
from multiprocessing import Pool
import logging
import sys
from classes.CladeParser import *
from classes.ProgramRunner import *
import Bio.SearchIO

version="0.01"

FORMAT = "%(asctime)-15s  %(message)s"

### TODO add this to configuration file
hmmer_db =  "/home/hputnam/Clade_Alignments/HMMER_ITS2_DB/All_Clades.hmm"

logging.basicConfig(format=FORMAT, level=logging.DEBUG)

def runInstance(myInstance):
   logging.warning(myInstance.dryRun())
   myInstance.run()

# Runs a command defined in params[0] passing it the parmas[1:]



def makeDirOrdie(dirPath):
   if not os.path.isdir(dirPath):
      os.makedirs(dirPath)
   else:
      pass
      #TODO; Uncomment after testing done
      #logging.error("Split fasta directory %s already exists " % hmmerOutputDir)
      #sys.exit()
      



def computeStats(args):
   print "------"
   Helpers.fastaStats(args.inFile)
   print "------"

def processClades(args, pool=Pool(processes=1)):

   logging.debug('Processing caldes for: %s ' % args.inFile.name)
   # Split fasta file
   # Put all the directories is at the same level as the inFile.
   fastaFilesDir = os.path.join(os.path.dirname(args.inFile.name), "fasta")
   fastaList = Helpers.splitFileBySample(args.inFile.name, args.samplesFile.name, fastaFilesDir)
   
   # Running HMMscan
   hmmerOutputDir =  os.path.join(os.path.dirname(args.inFile.name), "hmmer_output")
   makeDirOrdie(hmmerOutputDir)   
   logging.debug('Starting hmmscans for %s files ' % len(fastaList))
   #pool.map(runInstance, [ProgramRunner("HMMER_COMMAND", [ hmmer_db, os.path.join(fastaFilesDir,x), os.path.join(hmmerOutputDir,x.split(".")[0]) ] ) for x in fastaList])
   logging.debug('Done with hmmscans')

   #Parse HMMscan
   parsedHmmerOutputDir = os.path.join(os.path.dirname(args.inFile.name), "hmmer_parsedOutput")   
   makeDirOrdie(parsedHmmerOutputDir)
   logging.debug('Parsing Hmmer outputs for %s files ' % len(fastaList))
   #pool.map(runInstance, [CladeParser( "data/hmmer_output/"+x.split(".")[0]+".out", "data/hmmer_parsedOutput/"+x.split(".")[0], args.evalue) for x in fastaList])    
   logging.debug('Done Parsing Hmmer outputs for %s files ' % len(fastaList))

   # generate tables and pie-charts
   logging.debug("Generating formatted output")
   makeCladeDistribTable( args.samplesFile.name, os.path.join(os.path.dirname(args.inFile.name),"hmmer_parsedOutput"))   
   generateCladeBreakdown(args.samplesFile.name, os.path.join(os.path.dirname(args.inFile.name),"hmmer_parsedOutput"), "HIT", 4)
   logging.debug("Done Generating formatted output")
   

   logging.debug('Done with Clade run')


def main(argv):
   

   # Pool of threads to use. One by default


   # PARENT PARSER PARAMS
   parser = argparse.ArgumentParser(description="symTyper Description", epilog="symTyper long text description")
   parser.add_argument('-v', '--version', action='version', version='%(prog)s '+version)
   

   #TODO: Chnage the default to 1 after testing
   parser.add_argument('-t', '--threads', type=int, default =5)
   subparsers = parser.add_subparsers(dest='action', help='Available commands')

   ## CLADE
   parser_clade = subparsers.add_parser('clade')
   parser_clade.add_argument('-i', '--inFile', type=argparse.FileType('r'), required=True, help=" Input fasta file ")
   parser_clade.add_argument('-s', '--samplesFile', type=argparse.FileType('r'), required=True, help=" Input fasta file ")
   parser_clade.add_argument('-e', '--evalue', type=float, default=1e-20)
   parser_clade.add_argument('-d', '--evalDifference', type=float, default=1e5, help="Eval difference between first and second hits")
   

   parser_clade.set_defaults(func=processClades)

   ## INPUT FILE STATS
   parser_stats = subparsers.add_parser('stats')
   parser_stats.add_argument('-i', '--inFile', type=argparse.FileType('r'), required=True, help=" Input fasta file ")
   parser_stats.set_defaults(func=computeStats)


   args = parser.parse_args()

   print "Running with %s threads" % args.threads
   pool = Pool(processes=args.threads)

   logging.debug("Initial ARGS are:")   
   logging.debug(args)


   args.func(args, pool)   



if __name__ == "__main__":
   main(sys.argv)
