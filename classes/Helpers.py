from Bio import SeqIO
from collections import Counter
import os
import sys


# TODO THESE FUNCTION DO NOT NEED TO BE IN CLASS OR STATIC

class Helpers:
      @staticmethod
      def fastaStats(inFile):
            print "Computing stats for %s " % inFile.name

      @staticmethod
      def splitFileBySample(inFile, samplesDescFile, splitFastaDir):
            ## Strcuture of the sequence names is sample::id

            # create dir if not exists
            if not os.path.isdir(splitFastaDir):
                  os.makedirs(splitFastaDir)
            else:
                  # TODO after testing remove pass and uncomment die
                  pass
                  #sys.exit("split fasta disrectory exists")
            samples= []
            # For each sample name, get all its associated ids
            # and print the sequences into individuals files
            for sample in open(samplesDescFile, 'r'):
                  sample = sample.rstrip()
                  record_dict = SeqIO.index(inFile, "fasta")
                  sampleSeqsIds = [x for x in record_dict.keys() if x.startswith(sample+"::")] 
                  seqsRecords = [record_dict[x] for x in sampleSeqsIds]
                  SeqIO.write(seqsRecords, open(os.path.join(splitFastaDir, sample+".fasta"), 'w'), "fasta")
                  samples.append(sample+".fasta")
            
            # return all the samples individuals filenames
            # does not warrant its variable name but low overhead
            return samples


def getNumberLines(inFile):
      with open(inFile) as f:
            return len([1 for i in f])



def makeCladeDistribTable(samplesDescFile, parsedHmmerOutputDir):
      print "generating stats for samples.ids %s and outputs in %s " % (samplesDescFile, parsedHmmerOutputDir)

      cladeDistFileName = "ALL_counts.tsv"
      cladeDistFile = open(os.path.join(parsedHmmerOutputDir, cladeDistFileName), "w");

      outputs = ["HIT", "NOHIT", "LOW", "AMBIGUOUS"]
      cladeDistFile.write("Sample\t"+"\t".join(outputs)+"\n")
      
      with open(samplesDescFile) as sampleFile:
            for sample in sampleFile: 
                  sample = sample.rstrip()
                  cladeDistFile.write(sample+"\t"+"\t".join([ str(getNumberLines(os.path.join(parsedHmmerOutputDir,sample,inFile))) for inFile in outputs ])+"\n")
      cladeDistFile.close()


def generateCladeBreakdown(samplesDescFile, parsedHmmerOutputDir, fileName, field):
      cladeBreakdownFileName = "DETAILED_counts.tsv"
      cladeBreakdownFile = open(os.path.join(parsedHmmerOutputDir, cladeBreakdownFileName), "w");
      counts = {}
      with open(samplesDescFile) as sampleFile:
            for sample in sampleFile:
                  sample = sample.rstrip()
                  counts[sample] = Counter([l.split("\t")[field-1] for l in open(os.path.join( parsedHmmerOutputDir, sample,fileName))])

      # set of all the clades in the file            
      clades =  list(set([item for sublist in map(list, counts.values()) for item in sublist]))
      #Output Format
      myFormat = "{0:10}"+" ".join(["{"+str(i+1)+":30}" for i in range(len(clades))])
      print >> cladeBreakdownFile, myFormat.format("sample", *clades)


      with open(samplesDescFile) as sampleFile:
            for sample in sampleFile:
                  sample = sample.rstrip()
                  print >> cladeBreakdownFile, myFormat.format(sample, *[str(counts[sample][sam]) for sam in clades])

      cladeBreakdownFile.close()


      











