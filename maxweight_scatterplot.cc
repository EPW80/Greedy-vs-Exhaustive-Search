#include <fstream>
#include <iostream>
#include <iomanip>
#include <fstream>

#include "maxweight.hh"
#include "timer.hh"

using namespace std;

int main()
{
  ofstream greedy("greedy_detailed.csv");
  greedy << "n,execution_time_sec,weight_achieved,calories_used,items_selected" << endl;
  greedy << fixed << setprecision(10);

  auto all_foods = load_food_database("food.csv");
  auto filtered_foods = filter_food_vector(*all_foods, 1, 2500, all_foods->size());

  for(int i = 0; i < 2000; i++)
  {
    int n = i + 1;
    auto small_foods = filter_food_vector(*filtered_foods, 1, 2000, n);

    Timer timer;
    auto solution = greedy_max_weight(*small_foods, 2000);
    double total_calories, total_weight;
    sum_food_vector(*solution, total_calories, total_weight);
    greedy << n << "," << timer.elapsed() << ","
           << total_weight << "," << total_calories << ","
           << solution->size() << endl;
  }
  greedy.close();

  ofstream exhaustive("exhaustive_detailed.csv");
  exhaustive << "n,execution_time_sec,weight_achieved,calories_used,items_selected" << endl;
  exhaustive << fixed << setprecision(10);

  for(int i = 0; i < 50; i++)
  {
    int n = i + 1;
    auto small_foods = filter_food_vector(*filtered_foods, 1, 2000, n);

    Timer timer;
    auto solution = exhaustive_max_weight(*small_foods, 2000);
    double total_calories, total_weight;
    sum_food_vector(*solution, total_calories, total_weight);
    exhaustive << n << "," << timer.elapsed() << ","
              << total_weight << "," << total_calories << ","
              << solution->size() << endl;
  }
  exhaustive.close();
}
