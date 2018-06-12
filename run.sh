mkdir -p results/

TMP=results/tmp
mkdir -p $TMP

WILLIAMS=./tools/significance-williams/williams-sig.neg.sh
WILLIAMS_SP=./tools/significance-williams/williams-sig.neg.spearman.sh



for type in expected_wins trueskill ; do
    echo ""
    echo "--------------------------------------------------------------------------"
    echo "system-Level evaluation ($type)"
    echo "--------------------------------------------------------------------------"
    python3 scripts/system_correlation.py --human scores/system_scores_humans/$type.txt.gz --metrics scores/system_scores_metrics/*.gz --tablefmt orgtbl 2>&1 | tee results/sys.$type.txt

    echo -e "METRIC\tLP\tTESTSET\tSYSTEM\tSCORE" > $TMP/metrics.ranking.wmt.header.txt
    zcat scores/system_scores_metrics/*.gz >> $TMP/metrics.ranking.wmt.header.txt
    echo -e "METRIC\tLP\tTESTSET\tSYSTEM\tSCORE" > $TMP/$type.ranking.wmt.header.txt
    zcat scores/system_scores_humans/$type.txt.gz | sed "s|human|HUMAN|g" >> $TMP/$type.ranking.wmt.header.txt
    echo "--------------------------------------------------------------------------"
    echo "William's significance tests - Pearson ($type)"
    echo "--------------------------------------------------------------------------"

    bash $WILLIAMS src-trg $TMP/$type.ranking.wmt.header.txt $TMP/metrics.ranking.wmt.header.txt results/sys.$type.pearson.williams_test

    tail -n 5 results/sys.$type.pearson.williams_test/williams-results.src-trg
    echo "--------------------------------------------------------------------------"
    echo "William's significance tests - Spearman ($type)"
    echo "--------------------------------------------------------------------------"

    bash $WILLIAMS_SP src-trg $TMP/$type.ranking.wmt.header.txt $TMP/metrics.ranking.wmt.header.txt results/sys.$type.spearman.williams_test
    tail -n 5 results/sys.$type.spearman.williams_test/williams-spearman-results.src-trg


done

echo ""
echo "--------------------------------------------------------------------------"
echo "Sentence-Level Evaluation (Expanded)"
echo "--------------------------------------------------------------------------"
python3 scripts/sentence_correlation.py --judgments scores/sentence_pairwiseranks_humans/expanded.csv.gz --metrics scores/sentence_scores_metrics/*.gz --tablefmt orgtbl | tee results/sent.expanded.txt

echo ""
echo "--------------------------------------------------------------------------"
echo "Sentence-Level Evaluation (Unexpanded)"
echo "--------------------------------------------------------------------------"
python3 scripts/sentence_correlation.py --judgments scores/sentence_pairwiseranks_humans/unexpanded.csv.gz --metrics scores/sentence_scores_metrics/*.gz --tablefmt orgtbl | tee results/sent.unexpanded.txt
echo "--------------------------------------------------------------------------"

rm -r $TMP
