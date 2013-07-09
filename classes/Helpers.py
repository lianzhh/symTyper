from Bio import SeqIO
import os
import sys
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
