
import os
import sys
from collections import Counter

class CD_HitParser():
    MIN_NUM_SEQS = 3;
    #samplesNames = samples
    def __init__(self, samplesFile, repsClustersFile, samplesClustDir, multiplesDir):
        """
                #clusterSequences   {CL_ID:[seq1Id, seq2Id, ...], CL_ID:[seq1Id, ...], ... }
                #clusters       {CL_ID:{subtype_1:count, ...}}
                #sequences     {seq1Id:CL_ID, seq1Id:CL_ID, ... }
        """
        self.samplesClustDir = samplesClustDir
        self.repsClustersFile = repsClustersFile
        self.multiplesDir = multiplesDir

        self.samples =  [sample.rstrip() for sample  in open(samplesFile, 'r')] 
        # clusterSequences
        self.reps_clusterSequences= {} #{"CL_1": ["X1::29010", "X23::112", ...], "CL_2": ["X3::110", "X11::191", ...]}
        # clusters       
        self.reps_clusterSubtypeCounts= {} ## {"CL_1" : {"X1": 2, "X2": 10, ...}, "CL_2" : {"X1": 3, "X3": 1, ...}, ...}
        # sequences
        self.reps_sequenceCluster= {} ## {"X1::1": "CL_1" , "X2::1": "CL_2", ... }
        self.__initRepsDicts__(samplesFile)


        # This one is similar to self.reps_clusterSequences, except that it describes the clusters in the first clustering iteration
        #{"X1": {"CL_1":\["X1::1503",'X1::1403" ...], "CL_2":\["X1::4", "X1::167"]}}
        self.sample_clustersSeqs ={}
        # This one is similar to self.reps_sequenceCluster, except that it describes the sequences in the first clustering iteration
        # {"X1" : {"X1::1": "CL_1","X1::23" : "CL_2", ... }, "X2": {"X2:11", "CL_78", ...} ...}
        self.sample_sequenceCluster = {}

        for sample in self.samples:
            self.__initSamplesDicts__(sample)

    def __initSamplesDicts__(self, sample):
        """
        process the clusts file for one sample
        """
        clusterId = ""
        self.sample_clustersSeqs[sample]={}
        self.sample_sequenceCluster[sample]={}
        

        with open(os.path.join(self.samplesClustDir, sample+'.clstr'),'r' ) as sampleClusters:
            for line in sampleClusters:
                line = line.rstrip()
                if line.startswith(">"):
                    clusterId = "CL_"+line.split()[1]
                    self.sample_clustersSeqs[sample][clusterId] = []
                else:
                    seq = line.split()[2][1:-3]
                    self.sample_clustersSeqs[sample][clusterId].append(seq)
                    self.sample_sequenceCluster[sample][seq] = clusterId 


    def __initRepsDicts__(self, samplesFile):
        """
        Process the clusters file for the reps.
        """
        clusterId = ""

        with open(self.repsClustersFile,'r' ) as repsClusters:
            for line in repsClusters:
                line = line.rstrip()
                if line.startswith(">"):
                    clusterId = "CL_"+line.split()[1]
                    self.reps_clusterSubtypeCounts[clusterId] = {}
                    self.reps_clusterSequences[clusterId] = []
                else:
                    seq = line.split()[2][1:-3]
                    subType = seq.split("::")[0]
                    self.reps_clusterSequences[clusterId].append(seq)
                    self.reps_clusterSubtypeCounts[clusterId][subType]  = self.reps_clusterSubtypeCounts[clusterId].get(subType ,0) + 1
                    self.reps_sequenceCluster[seq] = clusterId


    def __filterSeqs__(self):
        """ We chck cluster to which seq belongs
        and make sure the cluster has seqs from at least 3 samples
        if it does, the seqeunces is kept """
        passed = []
        for seq in self.reps_sequenceCluster:
            clusterId = self.reps_sequenceCluster[seq]
            if len(self.reps_clusterSubtypeCounts[clusterId]) >= self.MIN_NUM_SEQS:
                passed.append(seq)
        return passed


    def __initSeqSubtypes__(self):
        # {'X1::1234': ['subtype_1", "subtype_2",...], ...}
        sSubtypes={}
        for sample in self.samples:
            # open file exists and add subtypes
            if os.path.exists(os.path.join(self.multiplesDir, sample+".out")):
                for line in open(os.path.join(self.multiplesDir, sample+".out"), 'r'):
                    line = line.rstrip()
                    data = line.split()
                    sSubtypes[data[0]] = data[1:]
        return sSubtypes

    def __computeEffectiveRange__(self, counts):
        sortedList = sorted(counts, reverse=True)
        


         my @sortedList = sort {$b <=> $a} @_;
    my ($start, $end) = (1, $sortedList[0]);
    print "Sorted list is: @sortedList\n";

    foreach my $val (@sortedList[1..$#sortedList]){
        if ($val > $start){
            $start = $start + 1.0/2 * ((1.0 * $val)/$end) * ($end - $start + 1);


            # USE ONLY FOR DEBUG                                                                                                                                       
            print "new val is $val  and new start is $start\n";
            #<STDIN>;                                                                                                                                                  
        }
    }
    my $newStart = 1;
    foreach my $val (reverse(@sortedList)){
        $newStart = $val;
        last if $val >= $start;
    }
    return ($newStart, $end);
}


    def run(self):
        # only sequences that occue in a cluster with at least MIN_NUM_SEQS from other clusters pass
        passedSeqs = self.__filterSeqs__()
        seqSubtypes= self.__initSeqSubtypes__()

        
        #number of sequences in a cluster of reps + number of sequences in each of samples they represent
        nbSeqs=0
        # will keep a list of the sequences that were thus far processed
        processedSeqs = {}
        subtypeCounts = {}

        # We get one filtered seqeunce at a time. For each filterd sequence, the reps in its cluster
        # for each of the rep, we then process the sequences that were in its cluster at the sample level.
        for passedSeq in passedSeqs:
            # contains the subtupes associated with one cluster of reps (and their representees in the samples)
            subtypes = []

            if processedSeqs.has_key(passedSeq):
                print "%s was already found using %s " % (passedSeq, processedSeqs[passedSeq])
                continue

            clustId =  self.reps_sequenceCluster[passedSeq]


            print "###############################################################################";
            print "processing reps cluster id:%s " % clustId
            print passedSeq
            # we resolve all the rep sequences that belong to that cluster from which we selected the passedSeq
            for seq in self.reps_clusterSequences[clustId]:
                # Remove seq from later processing since it was found. 
                processedSeqs[seq]= clustId+"_"+passedSeq;
                # which sample does seq belong to?
                sample = seq.split("::")[0]
                clust = self.sample_sequenceCluster[sample][seq]
                # Which sequences are with seq in the sample  cluster file?
                print "\t"+seq
                for sampleSeq in self.sample_clustersSeqs[sample][clust]:
                    print "\t\t"+sampleSeq
                    nbSeqs+=1
                    # we collect all the subtypes that for all the sequences in the same cluster  
                    # for later computing the effective range
                    subtypes.extend(seqSubtypes[sampleSeq])
                print "\n"
            print "\n"


            subtypeCounts = dict(Counter(subtypes))
            # array of counts used to determine the effective lower and upper ranges
            counts=subtypeCounts.values()
        

            print "Cluster: %s\tnumSeq:%s\tsubtypes:%s\t" % (clustId, nbSeqs, " ".join(subtypes))
            for (k, v) in  subtypeCounts.items():
                print "%s\t%s" % (k, v),
            print"\n";

            #computer the effective range


    def dryRun(self):
        pass

