from time import clock

class VCBenchmark(object):
    # data consists of completed timers
    data = {}
    # open set consists of in progress timers. If the timer is never closed, it will not be included in output
    open_set = {}

    def __init__(self,):
        self.data = {}

    def start(self, tag = "", is_error = True):
        """ Start a timer for a given tag
        :param tag: Start the benchmark timer for the tag
        :param is_error: throws an exception when you don't properly close tags. Otherwise, set the end to the previous 
instance, and start a new instance
        :return:
        """

        start = clock()
        if tag in self.open_set:
            if is_error:
                raise Exception("attempted to start tag while one was already open")
            else:
                if tag not in self.data:
                    self.data[tag] = []
                self.data[tag].append(start - self.open_set[tag])
        self.open_set[tag] = start

    def stop(self, tag = "", is_error = True):
        """ Stop a timer for a given tag
        :param tag: End the benchmark timer for the tag
        :param is_error: throws an exception when you don't properly start tags before ending them. Otherwise, ignore 
this instance
        :return:
        """
        end = clock()
        if tag not in self.open_set:
            if is_error:
                raise Exception("attempted to end tag while one didn't exist")
            else:
                return
        if tag not in self.data:
            self.data[tag] = []
        self.data[tag].append(end - self.open_set[tag])
        del self.open_set[tag]

    def TimingAnalysisText(self):
        """ Returns text detailing the analysis of all timing events
        :return: Text of the analysis of all timing events
        """
        text = ""
        text += "%s TIMING ANALYSIS %s\n" % ("=" * 41,"=" * 41)
        text += "%- 51s% 8s% 10s% 10s% 10s% 10s\n" % ("EVENT","COUNT","MIN","AVERAGE","MAX","SUM")
        text += "%s\n" % ("=" * 99)
        for tag in sorted(self.data, key=lambda key: self.data[key]):
            count = len(self.data[tag])

            sumval = 0
            avgval = 0
            if count > 0:
                sumval = sum(self.data[tag])
                avgval = sumval / count

            minval = min(self.data[tag])
            maxval = max(self.data[tag])
            text += "%- 51s% 8d% 10.5f% 10.5f% 10.5f% 10.3f\n" % (tag ,count,minval,avgval,maxval,sumval)


        return text
    def PrintTimingAnalysis(self):
        """Prints text detailing the analysis of all timing events
        :return:
        """
        print(self.TimingAnalysisText())
