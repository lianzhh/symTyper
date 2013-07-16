#!/usr/bin/python
import sys
import argparse
import os
from classes.Helpers import *
from multiprocessing import Pool
import logging
import sys
from classes.CladeParser import *
from classes.HmmerFastaExtractor import *
from classes.ProgramRunner import *


import Bio.SearchIO
from Bio import SeqIO

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
   return dirPath 



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
   pool.map(runInstance, [ProgramRunner("HMMER_COMMAND", [ hmmer_db, os.path.join(fastaFilesDir,x), os.path.join(hmmerOutputDir,x.split(".")[0]) ] ) for x in fastaList])
   logging.debug('Done with hmmscans')

   #Parse HMMscan
   parsedHmmerOutputDir = os.path.join(os.path.dirname(args.inFile.name), "hmmer_parsedOutput")   

   print "---------"+parsedHmmerOutputDir+"--------"
   makeDirOrdie(parsedHmmerOutputDir)

   logging.debug('Parsing Hmmer outputs for %s files ' % len(fastaList))

   # making dirs in hmmer_parsedOutput with the sample names
   pool.map(makeDirOrdie, [ os.path.join(parsedHmmerOutputDir, x.split(".")[0]) for x in fastaList])    

   #TODO use os.path.join instead of "+"
   samples = [sample.rstrip() for sample  in open(args.samplesFile.name, 'r')]
   pool.map(runInstance, [CladeParser( os.path.join(hmmerOutputDir, sample+".out"), os.path.join(parsedHmmerOutputDir, sample), args.evalue) for sample in samples])    
   logging.debug('Done Parsing Hmmer outputs for %s files ' % len(fastaList))

   # generate tables and pie-charts
   logging.debug("Generating formatted output")
   makeCladeDistribTable( args.samplesFile.name, os.path.join(os.path.dirname(args.inFile.name),"hmmer_parsedOutput"))   
   generateCladeBreakdown(args.samplesFile.name, os.path.join(os.path.dirname(args.inFile.name),"hmmer_parsedOutput"), "HIT", 4)
   logging.debug("Done Generating formatted output")
   

   logging.debug('Done with Clade run')



def extractSeqsFromHits(args, pool):
   """
   extracts the sequences of each hmmer HIT file, in parallel, using the sample specific fasta file (/data/fasta/sample.fasta)
   define args 
   
   """
   logging.debug("Extracting Hits from hmmer_parsedOutput")
   samples = [sample.rstrip() for sample in open(args.samplesFile.name, 'r')]
   pool.map(runInstance, [HmmerFastaExtractor( os.path.join(args.splitFasta, sample+".fasta"), os.path.join(args.hmmerOutputs, sample, "HIT"), os.path.join(args.outputDir, sample+".fasta")) for sample in samples])
   logging.debug(" Done extracting Hits from hmmer_parsedOutput")
      

def processSubtype(args, pool):
   print "processing subtype"

   



def main(argv):
   

   # Pool of threads to use. One by default


   # PARENT PARSER PARAMS
   parser = argparse.ArgumentParser(description="symTyper Description", epilog="symTyper long text description")
   parser.add_argument('-v', '--version', action='version', version='%(prog)s '+version)
   

   #TODO: Chnage the default to 1 after testing
   parser.add_argument('-t', '--threads', type=int, default = 1)
   subparsers = parser.add_subparsers(dest='action', help='Available commands')

   ## CLADE
   parser_clade = subparsers.add_parser('clade')
   parser_clade.add_argument('-i', '--inFile', type=argparse.FileType('r'), required=True, help=" Input fasta file ")
   parser_clade.add_argument('-s', '--samplesFile', type=argparse.FileType('r'), required=True, help=" Samples file  ")
   parser_clade.add_argument('-e', '--evalue', type=float, default=1e-20)
   parser_clade.add_argument('-d', '--evalDifference', type=float, default=1e5, help="Eval difference between first and second hits")
   parser_clade.set_defaults(func=processClades)

   ## SUBTYPE
   parser_subtype = subparsers.add_parser('subtype')
   parser_subtype.add_argument('-i', '--inFile', type=argparse.FileType('r'), required=True, help=" Input sequences that passed the Clade")
   parser_subtype.add_argument('-s', '--samplesFile', type=argparse.FileType('r'), required=True, help=" Samples file ")
   parser_subtype.set_defaults(func=processSubtype)


   ## EXTRACTFASTA
   parser_extractFasta = subparsers.add_parser('extractFasta')
   parser_extractFasta.add_argument('-f', '--splitFasta', required=True, help=" split fasta file dir")
   parser_extractFasta.add_argument('-s', '--samplesFile', type=argparse.FileType('r'), required=True, help=" Samples file ")
   parser_extractFasta.add_argument('-d', '--hmmerOutputs', required=True, help=" hmmer ouput directory")

   parser_extractFasta.add_argument('-o', '--outputDir', type=makeDirOrdie, required=True, help=" Fasta ouput directory")
   parser_extractFasta.set_defaults(func=extractSeqsFromHits)
      



   ## INPUT FILE STATS
   parser_stats = subparsers.add_parser('stats')
   parser_stats.add_argument('-i', '--inFile', type=argparse.FileType('r'), required=True, help=" Input fasta file ")
   parser_stats.set_defaults(func=computeStats)





   args = parser.parse_args()

   print "Running with %s threads" % args.threads
   pool = Pool(processes=args.threads)



   # my arguments are
   logging.debug("Initial ARGS are:")   
   logging.debug(args)


   args.func(args, pool)   



if __name__ == "__main__":
   main(sys.argv)
