////////////////////////////////////////////////////////////////////////////////
// maxweight.hh
//
// Compute the set of foods that maximizes the weight in foods, within
// a given maximum calorie value with the greedy method or exhaustive search.
//
///////////////////////////////////////////////////////////////////////////////

#pragma once
#include <cassert>
#include <cmath>
#include <fstream>
#include <iostream>
#include <memory>
#include <queue>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>

// One food item available for purchase.
class FoodItem
{
  //
public:
  //
  FoodItem(const std::string &description, double calories, double weight_ounces) : _description(description), _calories(calories), _weight_ounces(weight_ounces)
  {
    assert(!description.empty());
    assert(calories > 0);
  }
  const std::string &description() const
  {
    return _description;
  }
  double calorie() const
  {
    return _calories;
  }
  double weight() const
  {
    return _weight_ounces;
  }

  //
private:
  // Human-readable description of the food, e.g. "spicy chicken breast". Must be non-empty.
  std::string _description;

  // Calories; Must be positive
  double _calories;

  // Food weight, in ounces; most be non-negative.
  double _weight_ounces;
};

// Alias for a vector of shared pointers to FoodItem objects.
typedef std::vector<std::shared_ptr<FoodItem>> FoodVector;

// Comparator to sort food items by their weight-per-calorie ratio in descending order
bool compareWeightPerCalorie(const std::shared_ptr<FoodItem> &a, const std::shared_ptr<FoodItem> &b)
{
  return (a->weight() / a->calorie()) > (b->weight() / b->calorie());
}

// Load all the valid food items from the CSV database
// Food items that are missing fields, or have invalid values, are skipped.
// Returns nullptr on I/O error.
std::unique_ptr<FoodVector> load_food_database(const std::string &path)
{
  std::unique_ptr<FoodVector> failure(nullptr);

  std::ifstream f(path);
  if (!f)
  {
    std::cout << "Failed to load food database; Cannot open file: " << path << std::endl;
    return failure;
  }

  std::unique_ptr<FoodVector> result(new FoodVector);

  size_t line_number = 0;
  for (std::string line; std::getline(f, line);)
  {
    line_number++;

    // First line is a header row
    if (line_number == 1)
    {
      continue;
    }

    std::vector<std::string> fields;
    std::stringstream ss(line);

    for (std::string field; std::getline(ss, field, '^');)
    {
      fields.push_back(field);
    }

    if (fields.size() != 3)
    {
      std::cout << "Failed to load food database: Invalid field count at line " << line_number << "; Want 3 but got " << fields.size() << std::endl
                << "Line: " << line << std::endl;
      return failure;
    }

    std::string
        descr_field = fields[0],
        calories_field = fields[1],
        weight_ounces_field = fields[2];

    auto parse_dbl = [](const std::string &field, double &output)
    {
      std::stringstream ss(field);
      if (!ss)
      {
        return false;
      }

      ss >> output;

      return true;
    };

    std::string description(descr_field);
    double calories, weight_ounces;
    if (
        parse_dbl(calories_field, calories) &&
        parse_dbl(weight_ounces_field, weight_ounces))
    {
      result->push_back(
          std::shared_ptr<FoodItem>(
              new FoodItem(
                  description,
                  calories,
                  weight_ounces)));
    }
  }

  f.close();

  return result;
}

// Convenience function to compute the total weight and calories in
// a FoodVector.
// Provide the FoodVector as the first argument
// The next two arguments will return the weight and calories back to
// the caller.
void sum_food_vector(
    const FoodVector &foods,
    double &total_calories,
    double &total_weight)
{
  total_calories = total_weight = 0;
  for (auto &food : foods)
  {
    total_calories += food->calorie();
    total_weight += food->weight();
  }
}

// Convenience function to print out each FoodItem in a FoodVector,
// followed by the total weight and calories of it.
void print_food_vector(const FoodVector &foods)
{
  std::cout << "*** food Vector ***" << std::endl;

  if (foods.size() == 0)
  {
    std::cout << "[empty food list]" << std::endl;
  }
  else
  {
    for (auto &food : foods)
    {
      std::cout << "Ye olde " << food->description() << " ==> "
                << "; calories = " << food->calorie() << "Weight of " << food->weight() << " ounces" << std::endl;
    }

    double total_calories, total_weight;
    sum_food_vector(foods, total_calories, total_weight);
    std::cout << "> Grand total calories: " << total_calories << std::endl
              << "> Grand total weight: " << total_weight << " ounces" << std::endl;
  }
}

// Filter the vector source, i.e. create and return a new FoodVector
// containing the subset of the food items in source that match given
// criteria.
// This is intended to:
//	1) filter out food with zero or negative weight that are irrelevant to // our optimization
//	2) limit the size of inputs to the exhaustive search algorithm since it // will probably be slow.
//
// Each food item that is included must have at minimum min_weight and
// at most max_weight.
//	(i.e., each included food item's weight must be between min_weight
// and max_weight (inclusive).
//
// In addition, the vector includes only the first total_size food items
// that match these criteria.
std::unique_ptr<FoodVector> filter_food_vector(
    const FoodVector &source,
    double min_weight,
    double max_weight,
    size_t total_size)
{
  // Create a new food vector to hold filtered items
  auto result = std::make_unique<FoodVector>();

  // If the requested total_size is 0 (or, hypothetically, negative which is prevented by using size_t), return the empty result immediately.
  if (total_size <= 0)
  {
    return result;
  }
  // Iterate over each food item in the source
  for (const auto &item : source)
  {
    // Check if the current item's weight falls within the specified range (min_weight to max_weight)
    // and if the result list has not yet reached the specified total_size.
    if (item->weight() >= min_weight && item->weight() <= max_weight && result->size() < total_size)
    {
      result->push_back(item);
    }
    // Break early if we have reached the desired size
    if (result->size() == total_size)
    {
      break;
    }
  }
  // Return the filtered list of food items
  return result;
}

// Compute the optimal set of food items with a greedy algorithm.
// Specifically, among the food items that fit within a total_calorie,
// choose the foods whose weight-per-calorie is greatest.
// Repeat until no more food items can be chosen, either because we've
// run out of food items, or run out of space.
std::unique_ptr<FoodVector> greedy_max_weight(const FoodVector &foods, double total_calorie)
{
  auto result = std::make_unique<FoodVector>();
  double currentCalories = 0.0;

  // Copy and sort the foods by weight-per-calorie ratio in descending order
  FoodVector sortedFoods(foods.begin(), foods.end());
  std::sort(sortedFoods.begin(), sortedFoods.end(), compareWeightPerCalorie);

  for (const auto &item : sortedFoods)
  {
    double itemCalories = item->calorie();
    if (currentCalories + itemCalories <= total_calorie)
    {
      result->push_back(item);
      currentCalories += itemCalories;
    }
    else
    {
      break; // Stop if the next item exceeds the calorie limit
    }
  }

  return result;
}

// Compute the optimal set of food items with a exhaustive search algorithm.
// Specifically, among all subsets of food items, return the subset
// whose weight in ounces fits within the total_weight one can carry and
// whose total calories is greatest.
// To avoid overflow, the size of the food items vector must be less than 64.
std::unique_ptr<FoodVector> exhaustive_max_weight(const FoodVector &foods, double total_calorie)
{
  double bestWeight = 0;
  std::vector<size_t> bestSubsetIndices;

  size_t totalSubsets = 1 << foods.size();

  for (size_t i = 0; i < totalSubsets; ++i)
  {
    double currentWeight = 0;
    double currentCalories = 0;
    std::vector<size_t> currentSubsetIndices;

    for (size_t j = 0; j < foods.size(); ++j)
    {
      if (i & (1 << j))
      {
        currentSubsetIndices.push_back(j);
        currentWeight += foods[j]->weight();
        currentCalories += foods[j]->calorie(); // Use the getter method
      }
    }

    if (currentCalories <= total_calorie && currentWeight > bestWeight)
    {
      bestWeight = currentWeight;
      bestSubsetIndices = std::move(currentSubsetIndices);
    }
  }

  auto bestSubset = std::make_unique<FoodVector>();
  for (auto index : bestSubsetIndices)
  {
    bestSubset->push_back(foods[index]);
  }

  return bestSubset;
}