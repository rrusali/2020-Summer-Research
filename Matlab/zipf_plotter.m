load("C:\Users\novar\Downloads\Research Stuff\Jupyter Notebooks\Data Exports\Additional Data\City Zipfs.mat")
zipf_data = all_data;

num_ranks = size(zipf_data,1);
colors = colormap(winter(10));

Balt = zipf_data{:,1};
DC   = zipf_data{:,2};
Denv = zipf_data{:,3};
LV   = zipf_data{:,4};
LA   = zipf_data{:,5};
Nash = zipf_data{:,7};
NYC  = zipf_data{:,8};
Pitt = zipf_data{:,9};
Rale = zipf_data{:,16};
SF   = zipf_data{:,17};

range = 1:num_ranks;
plot(1:num_ranks, 1./range,'--k','LineWidth',3)
hold on
plot(1:num_ranks, Balt,'o','MarkerSize',8,'MarkerEdgeColor',colors(1,:));
plot(1:num_ranks, DC,'o','MarkerSize',8,'MarkerEdgeColor',colors(2,:));
plot(1:num_ranks, Denv,'o','MarkerSize',8,'MarkerEdgeColor',colors(3,:));
plot(1:num_ranks, LV,'o','MarkerSize',8,'MarkerEdgeColor',colors(4,:));
plot(1:num_ranks, LA,'o','MarkerSize',8,'MarkerEdgeColor',colors(5,:));
plot(1:num_ranks, Nash,'o','MarkerSize',8,'MarkerEdgeColor',colors(6,:));
plot(1:num_ranks, NYC,'o','MarkerSize',8,'MarkerEdgeColor',colors(7,:));
plot(1:num_ranks, Pitt,'o','MarkerSize',8,'MarkerEdgeColor',colors(8,:));
plot(1:num_ranks, Rale,'o','MarkerSize',8,'MarkerEdgeColor',colors(9,:));
plot(1:num_ranks, SF,'o','MarkerSize',8,'MarkerEdgeColor',colors(10,:));

ax = gca;
ax.FontSize = 20; 

xlabel('k (ordinal rank by size)','FontName','Avenir Next','FontSize',22)
ylabel('s (normalized size)','FontName','Avenir Next','FontSize',22)

fig_legend = legend('s \sim k^{-1}','Baltimore','Washington D.C.','Denver','Las Vegas','Los Angeles','Nashville','New York City','Pittsburgh','Raleigh','San Francisco','FontSize',18,'FontName','Avenir Next', 'Location', 'Southwest')
fig_legend.NumColumns = 2;

set(gca, 'YScale', 'log');
set(gca, 'XScale', 'log');
set(gcf, 'position', [10,10,1600,600]);