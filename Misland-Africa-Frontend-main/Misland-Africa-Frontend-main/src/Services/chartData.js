export default {
  dataProcessor: ({ results, indicator }) => {
    if (process.env.DEV) console.log(indicator, " -------------- indicator in stats --------------", results.stats.mapping);
    let labels = []
    // labels = results.stats.mapping.map(stat => stat.label)
    results.stats.stats[0].stats.forEach(stat => {
      const found = results.stats.mapping.find(mapping => mapping.id === stat.key)
      labels.push(found.label)
    });
    const values = results.stats.stats[0].stats.map(stat => (stat.value / 10000).toFixed(2))
    const backgroundColor = results.stats.stats[0].stats.map(stat => {
      const color = results.stats.mapping.find(color => {
        let found = stat.label === color.label
        if (!found) found = parseInt(stat.label) === parseInt(color.val)
        return found;
      })
      return color.color
    })
    if (process.env.DEV) console.log("results ", { backgroundColor, labels, values });
    return {
      backgroundColor, labels, values,
      start_year: results.base,
      end_year: results.target,
    }
  },

  changeDataProcessor: ({ results, indicator }) => {
    if (process.env.DEV) console.log(indicator, "--------------- changeData processor ---------------", results);
    const labels = results.stats.map(stat => stat.label)
    const values = results.stats.map(stat => (stat.area / 10000).toFixed(2))
    // chart background colors
    const backgroundColor = results.stats.map(stat => {
      const color = indicator.colors.find(color => stat.change_type === color.change_type)
      return color?.color || "#f4f1da";
    });
    // ==================
    //     // / Extract from legend directly
    // const legendEntries = Object.values(results.legend || {});

    // const labels = legendEntries.map(entry => entry.label.trim());
    // const backgroundColor = legendEntries.map(entry => entry.color);

    // // If you still need values from stats
    // const values = results.stats.map(stat => (stat.area / 10000).toFixed(2))

    return {
      backgroundColor, labels, values, indicator
    }
  }

}
