import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class CookPage extends StatefulWidget {
  const CookPage({super.key});

  @override
  State<CookPage> createState() => _CookPageState();
}

class _CookPageState extends State<CookPage> {
  final TextEditingController _controller = TextEditingController();
  bool _isLoading = false;
  Map<String, dynamic> _results = {};

  void _reset() {
    setState(() {
      _controller.clear();
      _isLoading = false;
      _results = {};
    });
  }

  Future<void> _getResults() async {
    FocusManager.instance.primaryFocus?.unfocus();

    final input = _controller.text.trim();
    if (input.isEmpty) return;

    setState(() {
      _isLoading = true;
      _results = {};
    });

    try {
      final response = await http.get(
        Uri.parse('http://192.168.1.13:5000/process?input=${Uri.encodeComponent(input)}'),
      );

      if (response.statusCode == 200) {
        setState(() {
          _results = json.decode(response.body);
        });
      } else {
        setState(() {
          _results = {"error": "Something went wrong! Please try again."};
        });
      }
    } catch (e) {
      setState(() {
        _results = {"error": "Unable to connect to server. Please check your connection."};
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Widget _buildResultCard(String title, String content) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.black87,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              content,
              style: const TextStyle(
                fontSize: 15,
                color: Colors.black54,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResults() {
    if (_results.isEmpty) {
      return const SizedBox.shrink();
    }

    if (_results.containsKey('error')) {
      return Center(
        child: Card(
          color: Colors.red.shade50,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              _results['error'],
              style: TextStyle(
                color: Colors.red.shade700,
                fontSize: 16,
              ),
            ),
          ),
        ),
      );
    }

    return ListView(
      shrinkWrap: true,
      children: [
        _buildResultCard(
          'Foods',
          _results['foods'].join(', '),
        ),
        _buildResultCard(
          'Weights',
          '${_results['food_weights'].join(', ')} grams',
        ),
        _buildResultCard(
          'Nutrients',
          'Calories, Protein, Fat: ${_results['needed_nutrients'].join(', ')}',
        ),
        _buildResultCard(
          'Recipe',
          _results['recipe'] ?? 'No recipe found.',
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Recipe Finder",
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        elevation: 0,
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      TextField(
                        controller: _controller,
                        decoration: InputDecoration(
                          labelText: "Enter your meal description",
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                          filled: true,
                          fillColor: Colors.grey.shade50,
                        ),
                        maxLines: 3,
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton(
                              onPressed: _isLoading ? null : _getResults,
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 16),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8),
                                ),
                              ),
                              child: _isLoading
                                  ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                                  : const Text(
                                "Get Recipe",
                                style: TextStyle(fontSize: 16),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          IconButton(
                            onPressed: _reset,
                            icon: const Icon(Icons.refresh),
                            tooltip: 'Reset',
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              _buildResults(),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}